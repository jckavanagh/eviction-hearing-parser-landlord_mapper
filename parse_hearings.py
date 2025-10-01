"""
Module to get case details given case numbers.
To perform a scraper run, use: python parse_hearings.py name_of_csv_with_case_numbers
"""

import csv
import click
import logging
import sys
import simplejson

import scrapers
from typing import Any, Dict, List, Optional
from emailing import log_and_email

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


def get_ids_to_parse(infile: click.File) -> List[str]:
    """Gets a list of case numbers from the csv `infile`"""

    ids_to_parse = []
    reader = csv.reader(infile)
    for row in reader:
        ids_to_parse.append(row[0])
    return ids_to_parse


def parse_all_from_parse_filings(
    case_nums: List[str],
    scraper: Optional[scrapers.FakeScraper] = None,
    db: bool = True,
    county: str = "travis",
    showbrowser: bool = False,
) -> List[Dict[str, Any]]:
    """
    Gets case details for each case number in `case_nums` and sends the data to PostgreSQL.
    Logs any case numbers for which getting data failed.
    """
    if not scraper:
        # Get the scraper corresponding to the lowercase command line entry for county. Default to TravisScraper.
        county = county.lower()
        scraper = (
            scrapers.SCRAPER_NAMES[county]()
            if county in scrapers.SCRAPER_NAMES
            else scrapers.TravisScraper()
        )
    parsed_cases = []
    for tries in range(1, 6):
        try:
            parsed_cases = scraper.make_case_list(ids_to_parse=case_nums)
            return parsed_cases
        except Exception as e:
            logger.error(
                f"Failed to parse hearings on attempt {tries}. Error message: {e}"
            )
    return parsed_cases


# def persist_parsed_cases(cases: List[Dict[str, Any]]) -> None:
#     import persist

#     logger.info(
#         f"Finished making case list, now will send all {len(cases)} cases to SQL."
#     )

#     failed_cases = []
#     for parsed_case in cases:
#         try:
#             persist.rest_case(parsed_case)
#         except:
#             try:
#                 failed_cases.append(parsed_case.case_number)
#             except:
#                 logger.error(
#                     "A case failed to be parsed but it doesn't have a case number."
#                 )

#     if failed_cases:
#         error_message = f"Failed to send the following case numbers to SQL:\n{', '.join(failed_cases)}"
#         log_and_email(
#             error_message,
#             "Case Numbers for Which Sending to SQL Failed",
#             error=True,
#         )
#     logger.info("Finished sending cases to SQL.")

def persist_parsed_cases(cases: List[Dict[str, Any]]) -> None:
    import persist
    
    logger.info(f"Finished making case list, now will send all {len(cases)} cases to SQL.")
    
    success_count = 0
    failed_cases = []
    
    for i, parsed_case in enumerate(cases):
        try:
            persist.rest_case(parsed_case)
            success_count += 1
            if i % 10 == 0:  # Print progress every 10 cases
                print(f"Progress: {i}/{len(cases)} cases processed...")
        except Exception as e:
            print(f"ERROR persisting case {parsed_case.case_number}: {e}")
            # Print full error for FIRST failed case only
            if len(failed_cases) == 0:
                import traceback
                print("Full error traceback for first failed case:")
                traceback.print_exc()
            
            try:
                failed_cases.append(parsed_case.case_number)
            except:
                logger.error("A case failed to be parsed but it doesn't have a case number.")
    
    print(f"\nPersistence Summary:")
    print(f"✓ Successfully persisted: {success_count}/{len(cases)}")
    print(f"✗ Failed: {len(failed_cases)}/{len(cases)}")
    
    if failed_cases:
        error_message = f"Failed to send the following case numbers to SQL:\n{', '.join(failed_cases)}"
        log_and_email(error_message, "Case Numbers for Which Sending to SQL Failed", error=True)
    
    logger.info("Finished sending cases to SQL.")

@click.command()
@click.option("--infile", type=click.File(mode="r"), required=False)

@click.option("--outfile", type=click.File(mode="w"), required=False)
@click.option(
    "--county",
    type=click.Choice(scrapers.SCRAPER_NAMES, case_sensitive=False),
    default="travis",
)
@click.option(
    "--showbrowser / --headless",
    default=False,
    help="whether to operate in headless mode or not",
)
@click.option(
    "--db / --no-db",
    default=True,
    help="whether to persist the data to a db",
)
@click.option(
    "--db / --no-db",
    default=True,
    help="whether to persist the data to a db",
)
def parse_all(
    infile: Optional[click.File],
    outfile: Optional[click.File],
    county: Optional[click.STRING],
    showbrowser=False,
    db=True,
):
    """Same as `parse_all_from_parse_filings()` but takes in a csv of case numbers instead of a list."""

    ids_to_parse = get_ids_to_parse(infile)
    parsed_cases = parse_all_from_parse_filings(
        case_nums=ids_to_parse, showbrowser=showbrowser, db=db, county=county
    )
    if db:
        persist_parsed_cases(parsed_cases)
    if outfile:
        simplejson.dump(parsed_cases, outfile, default=dict)


if __name__ == "__main__":
    parse_all()