from app.services.scraper_service import run_dental_scraper_task

if __name__ == "__main__":
    print("Starting manual multi-site scraper run...")
    run_dental_scraper_task()
    print("Scraper run completed.")
