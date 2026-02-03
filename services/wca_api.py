"""WCA API service for executing queries and fetching data."""
import logging
import aiomysql
from typing import List, Dict, Any
from wcwidth import wcswidth
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger(__name__)


class WCAService:
    """Service for interacting with WCA database and executing queries."""

    def __init__(self):
        """Initialize the WCA service."""
        self.pool = None
        self.db_config = {
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'db': DB_NAME,
        }

    async def _get_pool(self):
        """Get or create database connection pool."""
        if self.pool is None:
            try:
                self.pool = await aiomysql.create_pool(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    user=self.db_config['user'],
                    password=self.db_config['password'],
                    db=self.db_config['db'],
                    minsize=1,
                    maxsize=10,
                    autocommit=True
                )
                logger.info("Database connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create database connection pool: {e}")
                raise
        return self.pool

    async def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query against the WCA database.

        Args:
            sql_query: SQL query string

        Returns:
            List of result dictionaries
        """
        logger.info(f"Executing query: {sql_query}")

        try:
            pool = await self._get_pool()

            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # Execute the query
                    await cursor.execute(sql_query)

                    # Fetch results
                    results = await cursor.fetchall()

                    # Convert to list of dicts (aiomysql.DictCursor already returns dicts)
                    result_list = [dict(row) for row in results]

                    logger.info(f"Query returned {len(result_list)} results")

                    # Post-process results to format times properly
                    result_list = self._post_process_results(result_list)

                    return result_list

        except Exception as e:
            logger.error(f"Error executing query: {e}", exc_info=e)
            return [{
                "error": "Execution failed",
                "message": str(e)
            }]

    def _post_process_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Post-process query results to format times and other WCA-specific data.

        Args:
            results: Raw query results

        Returns:
            Processed results
        """
        processed = []

        for row in results:
            processed_row = {}
            for key, value in row.items():
                # Format time results (WCA stores times in centiseconds)
                if key in ['best', 'average', 'value1', 'value2', 'value3', 'value4', 'value5', 'worldRecord', 'continentalRecord', 'nationalRecord']:
                    if isinstance(value, int) and value > 0:
                        processed_row[key] = self._format_time(value)
                    elif value == -1:
                        processed_row[key] = 'DNF'
                    elif value == -2:
                        processed_row[key] = 'DNS'
                    else:
                        processed_row[key] = value
                else:
                    processed_row[key] = value

            processed.append(processed_row)

        return processed

    def _format_time(self, centiseconds: int) -> str:
        """
        Format time in centiseconds to human-readable format.

        Args:
            centiseconds: Time in centiseconds (1/100th of a second)

        Returns:
            Formatted time string
        """
        if centiseconds == -1:
            return "DNF"
        elif centiseconds == -2:
            return "DNS"
        elif centiseconds == 0:
            return "-"

        # For 3x3x3 Multi-Blind, the format is special
        # We'll handle it as a regular number for now

        if centiseconds < 6000:  # Less than 60 seconds
            seconds = centiseconds / 100
            return f"{seconds:.2f}s"
        else:  # Minutes and seconds
            minutes = centiseconds // 6000
            remaining = (centiseconds % 6000) / 100
            return f"{minutes}:{remaining:05.2f}"

    def _display_width(self, text: str) -> int:
        """
        Calculate the display width of a string, accounting for Unicode characters.

        Args:
            text: String to measure

        Returns:
            Display width in terminal columns
        """
        width = wcswidth(text)
        # If wcswidth returns -1 (for control characters), fall back to len()
        return width if width >= 0 else len(text)

    def _pad_to_width(self, text: str, target_width: int) -> str:
        """
        Pad a string to a target display width, accounting for Unicode characters.

        Args:
            text: String to pad
            target_width: Target display width

        Returns:
            Padded string
        """
        current_width = self._display_width(text)
        padding_needed = target_width - current_width
        if padding_needed > 0:
            return text + (' ' * padding_needed)
        return text

    def format_results(self, results: List[Dict[str, Any]], max_results: int = 50) -> str:
        """
        Format query results for Discord display.

        Args:
            results: List of result dictionaries
            max_results: Maximum number of results to display

        Returns:
            Formatted string
        """
        if not results:
            return "No results found."

        # Check if it's an error result
        if len(results) == 1 and 'error' in results[0]:
            return f"Error: {results[0].get('message', 'Unknown error')}"

        # Limit results
        display_results = results[:max_results]

        if len(display_results) == 0:
            return "No results found."

        # Get column names from first result
        columns = list(display_results[0].keys())

        # Calculate optimal column widths using display width (accounts for Unicode)
        col_widths = {}
        for col in columns:
            # Start with column name display width
            max_width = self._display_width(str(col))
            # Check all data values for this column
            for row in display_results:
                value_width = self._display_width(str(row.get(col, "")))
                max_width = max(max_width, value_width)
            # Set max width (but cap at 50 to prevent extremely wide columns)
            col_widths[col] = min(max_width, 50)

        # Create formatted output
        lines = []
        lines.append("Results:")

        # Calculate total width for separator
        total_width = sum(col_widths.values()) + (len(columns) - 1) * 3  # 3 for " | "
        lines.append("=" * total_width)

        # Header
        header = " | ".join(self._pad_to_width(str(col), col_widths[col]) for col in columns)
        lines.append(header)
        lines.append("-" * total_width)

        # Data rows
        for row in display_results:
            values = [self._pad_to_width(str(row.get(col, "")), col_widths[col]) for col in columns]
            lines.append(" | ".join(values))

        if len(results) > max_results:
            lines.append(f"\n... and {len(results) - max_results} more results")

        return "\n".join(lines)

    async def close(self):
        """Close the database connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database connection pool closed")
