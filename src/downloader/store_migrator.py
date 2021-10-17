# Copyright (c) 2021 José Manuel Barroso Galindo <theypsilon@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# You can download the latest version of this tool from:
# https://github.com/MiSTer-devel/Downloader_MiSTer

class StoreMigrator:
    def __init__(self, migration_list, logger):
        self._migrations = migration_list
        self._logger = logger

    def migrate(self, local_store):
        current_version = local_store.get('migration_version', 0)
        for i in range(current_version, len(self._migrations), 1):
            if (self._migrations[i].version - 1) != i:
                raise WrongMigrationException('Migration error: (%s -1) != %s' % (self._migrations[i].version, i))

            self._logger.debug('Running migration version %s.' % self._migrations[i].version)
            self._migrations[i].migrate(local_store)

        local_store['migration_version'] = self.latest_migration_version()

    def latest_migration_version(self):
        return len(self._migrations)


def make_new_local_store(store_migrator):
    return {'dbs': {}, 'migration_version': store_migrator.latest_migration_version()}


def migrations():
    return [
        MigrationV1(),
        MigrationV2()
    ]


class MigrationV1:
    version = 1

    def migrate(self, local_store):

        #
        # create 'dbs' field
        #
        db_ids = list(local_store.keys())
        dbs = dict()
        for db_id in db_ids:
            dbs[db_id] = local_store[db_id]
            local_store.pop(db_id)
        
        local_store['dbs'] = dbs

        #
        # create 'zips' fields 
        #
        for db_id in local_store['dbs']:
            local_store['dbs'][db_id]['zips'] = dict()


class MigrationV2:
    version = 2

    def migrate(self, local_store):

        #
        # 'folders' from list to dict
        #
        for db_id in local_store['dbs']:
            local_store['dbs'][db_id]['folders'] = {folder: {} for folder in local_store['dbs'][db_id]['folders']}
            for zip_id in local_store['dbs'][db_id]['zips']:
                local_store['dbs'][db_id]['zips'][zip_id]['folders'] = {folder: {} for folder in local_store['dbs'][db_id]['zips'][zip_id]['folders']}


class WrongMigrationException(Exception):
    pass