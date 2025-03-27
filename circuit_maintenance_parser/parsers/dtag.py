# pylint: disable=disallowed-name
"""Circuit maintenance parser for Tata Email notifications."""

from typing import List, Dict, Any

from bs4.element import ResultSet  # type: ignore
from circuit_maintenance_parser.output import Impact
from circuit_maintenance_parser.parser import Html


class HtmlParserDTAG(Html):
    """Custom Parser for HTML portion of DTAG circuit maintenance notifications. The DTAG ICS attachment does not give the circuit IDs, so we need to parse the HTML portion."""

    def parse_html(self, soup: ResultSet) -> List[Dict]:
        """Parse Tata circuit maintenance email."""
        data: Dict[str, Any] = {
            "circuits": [],
        }
        # Get all the tables in the email.
        tables = soup.find_all("table")

        circuits: list = []

        # Column header we care about in the tables.
        circuit_column_header: str = "List of circuit(s)."

        # Don't want the first table with the circuits.
        count: int = 1

        # Circuit IDs are in the current table.
        circuits_coming: bool = False

        # Check through the tables to find what we want.
        for table in tables:
            # Get the column headers and look at them.
            column_headers = table.find_all("strong")
            for header in column_headers:
                if header.text == circuit_column_header:
                    # Skip first time we see it.
                    if count == 1:
                        count += 1
                        continue
                    circuits_coming = True
                    continue
                if circuits_coming:
                    # Now we're ready for the circuits and all we'll get here are circuit IDs.
                    # However, we don't want duplicates
                    if header.text not in circuits:
                        circuits.append(header.text)

        # Make list of circuit dicts
        circuits = [{"circuit_id": circuit, "impact": Impact.OUTAGE} for circuit in circuits]

        data["circuits"] = circuits
        return [data]
