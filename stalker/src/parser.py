import logging
import re
import html
import csv
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from stalker.src.models.wallet import Snapshot, Asset

logger = logging.getLogger(__name__)


def strip_tags(raw: str) -> str:
    return re.sub(r"<[^>]+>", "", raw).strip()


class Parser:
    def __init__(self, soup, name: str):
        self.soup = soup
        self.name = name
        self.text = str(soup)
        logger.info("Parser initialized")
        self.xml_blob = self._extract_xml_blob()
        self.rows = self._iter_asset_rows()
        logger.info("Page parsed successfully")

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

    def save_csv(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile = Path(f"{self.name}_{timestamp}.csv")
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
        logger.info(f"Saved {len(self.rows)} asset rows → {outfile}")

    def make_snapshot(self):
        logger.info("Parsing snapshot...")
        self.rows = self._iter_asset_rows()
        assets = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for cells in self.rows:
            name = cells[1][len(cells[1]) // 2 :]
            asset = Asset(
                name=name,
                units=float(cells[3].replace(",", ".")),
                average_purchase_price=float(cells[4].replace(",", ".")),
                current_price=float(cells[5].replace(",", ".")),
                value=float(cells[6].replace(",", ".")),
                assets_share=float(cells[7].replace(",", ".")),
                change=float(cells[8].replace(",", ".")),
                profit=float(cells[9].replace(",", ".")),
                investment_period=int(cells[10]),
                timestamp=timestamp,
            )
            assets.append(asset)
        snapshot = Snapshot(assets=assets)
        return snapshot
