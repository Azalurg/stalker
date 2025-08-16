import argparse
import sys
import logging
from datetime import datetime

from dotenv import load_dotenv

from stalker.src.db import Store
from stalker.src.notifier import Notifier
from stalker.src.models.wallet import Wallet
from stalker.src.scraper import Scraper
from stalker.src.parser import Parser


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logbook", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def snapshots_differ(old_snapshot: dict, new_snapshot: dict) -> bool:
    """Compare two snapshots to detect changes in assets."""
    old_assets = {a["name"]: a["units"] for a in old_snapshot.get("assets", [])}
    new_assets = {a["name"]: a["units"] for a in new_snapshot.get("assets", [])}

    return old_assets != new_assets


def process_snapshot(store: Store, wallet_name: str, snapshot, logger):
    """Process and store a wallet snapshot, detecting changes from the last one."""
    snapshot_data = snapshot.as_dict()

    wallet_doc = store.find_wallet_by_name(wallet_name)

    if not wallet_doc:
        logger.info(f"Wallet '{wallet_name}' not found. Creating new one.")
        new_wallet = Wallet(
            name=wallet_name,
            url="",
            snapshots=[snapshot_data],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        new_wallet.store(store.db)
        logger.info("New wallet created with first snapshot.")
        return True

    old_snapshots = wallet_doc.get("snapshots", [])
    last_snapshot = old_snapshots[-1] if old_snapshots else None

    if not last_snapshot:
        logger.info(f"Wallet '{wallet_name}' has no snapshots — adding first one.")
        wallet_doc["snapshots"] = [snapshot_data]
        wallet_doc["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store.db.save(wallet_doc)
        return True

    if snapshots_differ(last_snapshot, snapshot_data):
        logger.info(
            f"Changes detected in wallet '{wallet_name}'. Adding new snapshot..."
        )
        wallet_doc["snapshots"].append(snapshot_data)
        wallet_doc["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store.db.save(wallet_doc)
        # send_update_message(wallet_name, last_snapshot, snapshot_data)
        return True
    else:
        logger.info(f"No changes in wallet '{wallet_name}'. No update needed.")
        return False


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Stalker - Wallet monitoring tool")
    parser.add_argument("--url", help="URL of the webpage to scrape", required=True)
    parser.add_argument("--name", help="Wallet name", required=True)
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=== STALKER STARTED ===")

    load_dotenv()

    notifier = Notifier()
    notifier.start_server()
    notifier.send_email("Stalker started", "Stalker service has been started successfully.")
    notifier.quit_server()

    exit()

    try:
        url = args.url
        wallet_name = args.name

        # Step 1: Scrape webpage
        logger.info(f"Starting scraping webpage: {url}")
        scraper = Scraper()
        soup = scraper.fetch_page(url)
        if soup is None:
            logger.error("Failed to fetch the webpage")
            sys.exit(1)

        # Step 2: Parse the content and create snapshot
        parser = Parser(soup, wallet_name)
        snapshot = parser.make_snapshot()

        # Step 3: Process and store snapshot
        store = Store(username="admin", password="password", dbname="stalker")
        process_snapshot(store, wallet_name, snapshot, logger)

    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
