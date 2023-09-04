from notion_interface import ModianStarPage, get_today
from modian_interface import get_modian_star
from time import sleep
import os

sleep_time = 60 * 60 * 24
database_id = os.environ["NOTION_DATABASE_ID"]

if __name__ == "__main__":
    modian_star_page = ModianStarPage(database_id)
    while True:
        print("Trying to get modian star...")
        star_count = get_modian_star()
        print("Modian star count = ", star_count)

        try:
            print("Inserting to notion...")
            modian_star_page.create_new_modian_star_page(get_today(), star_count)
        except Exception as e:
            print(e)
            print("Fail to insert to notion!")

        # DEBUG USE
        # break
        print("Sleep for 24 hours")
        sleep(sleep_time)
