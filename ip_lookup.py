import os
from geoip2 import database
import requests
from decouple import config
import tarfile
import shutil

ROOT_DB_PATH = os.path.dirname(__file__)
DB_FILE_PATH = os.path.join(ROOT_DB_PATH, 'db/GeoLite2-City.mmdb')


class GeoLocation:
    def __init__(self):
        """
        Example :
        geo_loc = GeoLocation()
        ip_address = '8.8.8.8'
        location = geo_loc.lookup_ip(ip_address)
        print(location)
        geo_loc.close()
        """
        self.update_db()
        self.reader = database.Reader(DB_FILE_PATH)

    def update_db(self):
        db_url = "https://download.maxmind.com/app/geoip_download"

        if not os.path.exists(DB_FILE_PATH):
            print('Downloading GeoLite2 database...')
            # Download the database
            response = requests.get(db_url, params={'edition_id': "GeoLite2-City", 'license_key': config('MAXMIND_LICENCE_KEY'), 'suffix': 'tar.gz'},
                                    stream=True)
            with open(ROOT_DB_PATH + '.tar.gz', 'wb') as f:
                f.write(response.raw.read())
            # Uncompress the database
            with tarfile.open(ROOT_DB_PATH + '.tar.gz') as tar:
                tar.extractall()
                # Rename extracted folder to db
                for info in tar:
                    if info.isdir():
                        shutil.rmtree("db", ignore_errors=True)
                        os.rename(src=info.name, dst="db")

            # Delete the compressed database file
            os.remove(ROOT_DB_PATH + '.tar.gz')

    def lookup_ip(self, ip_address: str) -> dict:
        """
        Lookup and ip address. This method is using the offline version of MaxMind Cities Database.
        :param ip_address:
        :return:
        """
        response = self.reader.city(ip_address)
        return {
            'country': response.country.name,
            'state/province': response.subdivisions.most_specific.name,
            'city': response.city.name,
            'postal code': response.postal.code,
            'latitude': response.location.latitude,
            'longitude': response.location.longitude
        }

    def close(self):
        self.reader.close()
