import logging
import re
import html
import csv
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def strip_tags(raw: str) -> str:
    return re.sub(r"<[^>]+>", "", raw).strip()


class Parser:
    def __init__(self, soup, name: str):
        self.soup = soup
        self.name = name
        self.text = str(soup)
        self.xml_blob = self._extract_xml_blob()
        logger.info("Parser initialized")

    def parse_html(self):
        self.rows = self._iter_asset_rows()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path(f"{self.name}_{timestamp}.csv")
        self._save_csv(out_path)
        logger.info(f"Saved {len(self.rows)} asset rows → {out_path}")

    def _extract_xml_blob(self) -> str:
        m = re.search(r'mygrid\.parse\("(?P<xml>.*?)"\s*\);\s*', self.text, re.DOTALL)
        if not m:
            raise RuntimeError("Could not find mygrid.parse( … ) block in content.")

        return html.unescape(m.group("xml"))

    def _iter_asset_rows(self):
        root = ET.fromstring(self.xml_blob)
        rows = []

        for row in root.findall(".//row"):
            cells = [strip_tags(cell.text or "") for cell in row.findall("cell")]

            if len(cells) < 11:
                logger.warning(f"Skipping row with insufficient cells: {cells}")
                continue

            asset_name = cells[1]

            if any(x in asset_name for x in ["Dywidenda", "Gotówka", "Total"]):
                continue

            rows.append(cells)

        return rows

    def _save_csv(self, outfile: Path):
        logger.info(f"Saving data to CSV file: {outfile}")

        headers = [
            "Asset",
            "Daily Change [%]",
            "Units",
            "Average Purchase Price [PLN]",
            "Current Price [PLN]",
            "Value [PLN]",
            "Asset Share [%]",
            "Change [%]",
            "Profit [PLN]",
            "Investment Period [days]",
        ]

        with outfile.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            for cells in self.rows:
                writer.writerow(
                    [
                        cells[1],  # Asset
                        cells[2],  # Daily Change %
                        cells[3],  # Units
                        cells[4],  # Average Purchase Price
                        cells[5],  # Current Price
                        cells[6],  # Value
                        cells[7],  # Asset Share
                        cells[8],  # Change %
                        cells[9],  # Profit
                        cells[10],  # Investment Period
                    ]
                )
