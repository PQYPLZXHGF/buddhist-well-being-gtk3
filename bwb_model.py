import sqlite3
import csv


def get_schema_version(i_db_conn):
    t_cursor = i_db_conn.execute("PRAGMA user_version")
    return t_cursor.fetchone()[0]

def set_schema_version(i_db_conn, i_version_it):
    i_db_conn.execute("PRAGMA user_version={:d}".format(i_version_it))

def initial_schema_and_setup(i_db_conn):
    i_db_conn.execute(
        "CREATE TABLE " + DbSchemaM.ObservancesTable.name + "("
        + DbSchemaM.ObservancesTable.Cols.list_pos + " INTEGER" + " PRIMARY KEY" + ", "
        + DbSchemaM.ObservancesTable.Cols.short_name + " TEXT" + ", "
        + DbSchemaM.ObservancesTable.Cols.sutra_text + " TEXT"
        + ")"
    )

    i_db_conn.execute(
        "CREATE TABLE " + DbSchemaM.KarmaTable.name + "("
        + DbSchemaM.KarmaTable.Cols.observance_id + " INTEGER REFERENCES " + DbSchemaM.ObservancesTable.name + ", "
        + DbSchemaM.KarmaTable.Cols.list_pos + " INTEGER" + ", "
        + DbSchemaM.KarmaTable.Cols.description + " TEXT" + ", "
        + " PRIMARY KEY (" + DbSchemaM.KarmaTable.Cols.list_pos + ", "
        + DbSchemaM.KarmaTable.Cols.observance_id + ")"
        + ")"
    )

    i_db_conn.execute(
        "CREATE TABLE " + DbSchemaM.DiaryTable.name + "("
        + DbSchemaM.DiaryTable.Cols.date_added + " INTEGER PRIMARY KEY" + ", "
        + DbSchemaM.DiaryTable.Cols.observance_id + " INTEGER REFERENCES " + DbSchemaM.ObservancesTable.name + ", "
        + DbSchemaM.DiaryTable.Cols.karma_id + " INTEGER REFERENCES " + DbSchemaM.KarmaTable.name + ", "
        + DbSchemaM.DiaryTable.Cols.notes + " TEXT"
        + ")"
    )
    # db_cursor.execute("DROP TABLE IF EXISTS " + DbSchemaM.DiaryTable.name)

    # Adding observances
    t_observances_lt = [
        (0, "Friends of virtue", "Foster relations with people of virtue and avoid the path of degradation"),
        (1, "Environment", "Live in an environment that is conducive to spiritual practice and builds good character"),
        (2, "Learning",
         "Foster opportunities to learn more about the Dharma, the precepts, and your own trade in greater depth"),
        (3, "Caring", "Take the time to care well for your parents, spouse, and children"),
        (4, "Sharing", "Share time, resources, and happiness with others"),
        (5, "Cultivating Virtue", "Foster opportunities to cultivate virtue. Avoid alcohol and gambling"),
        (6, "Gratitude", "Cultivate humility, gratitude, and simple living"),
        (7, "Monks", "Seek opportunities to be close to bhikkhus in order to study the Way"),
        (8, "Four Noble Truths", "Live a life based on the Four Noble Truths"),
        (9, "Meditation", "Learn how to meditate in order to release sorrows and anxieties")
    ]
    i_db_conn.executemany(
        "INSERT INTO " + DbSchemaM.ObservancesTable.name
        + " VALUES (?, ?, ?)", t_observances_lt
    )
    ''' Meditera, Knäövningar, Rörelseövningar, Fråga Pappa vad som varit roligt idag!'''

def upgrade_1_2(i_db_conn):
    pass

upgrade_steps = {
    1: initial_schema_and_setup
    #  2: upgrade_1_2
}


class DbHelperM(object):
    DATABASE_NAME = "bwb_database_file.db"
    __db_connection = None  # "Static"

    # def __init__(self):

    @staticmethod
    def get_db_connection():
        if DbHelperM.__db_connection is None:
            DbHelperM.__db_connection = sqlite3.connect(DbHelperM.DATABASE_NAME)

            ###db_connection = DbHelperM.get_db_connection(self)

            # Very good upgrade explanation:
            # http://stackoverflow.com/questions/19331550/database-change-with-software-update
            # More info here: https://www.sqlite.org/pragma.html#pragma_schema_version

            t_current_db_ver_it = get_schema_version(DbHelperM.__db_connection)
            t_target_db_ver_it = max(upgrade_steps)
            for upgrade_step_it in range(t_current_db_ver_it + 1, t_target_db_ver_it + 1):
                if upgrade_step_it in upgrade_steps:
                    upgrade_steps[upgrade_step_it](DbHelperM.__db_connection)
                    set_schema_version(DbHelperM.__db_connection, upgrade_step_it)

            DbHelperM.__db_connection.commit()

            # TODO: Where do we close the db connection? (Do we need to close it?)
            # http://stackoverflow.com/questions/3850261/doing-something-before-program-exit

        return DbHelperM.__db_connection


class DbSchemaM:

    class ObservancesTable:
        name = "observances"

        class Cols:
            list_pos = "list_pos"  # Key
            short_name = "short_name"
            sutra_text = "sutra_text"

    class KarmaTable:
        name = "karma"

        class Cols:
            list_pos = "list_pos"  # Key
            description = "description"
            observance_id = "observance_id"  # Ref, Key

    class DiaryTable:
        name = "diary"

        class Cols:
            date_added = "date_added"  # Key
            notes = "notes"
            observance_id = "observance_id" # Ref
            karma_id = "karma_id" # Ref


class ObservanceM:
    def __init__(self, i_short_name_sg, i_sutra_text_sg):
        self.short_name_sg = i_short_name_sg
        self.sutra_text_sg = i_sutra_text_sg

    @staticmethod
    def insert(i_cursor, i_short_name_sg, i_sutra_text_sg):
        i_cursor.execute(
            "INSERT INTO " + DbSchemaM.ObservancesTable.name + "("
            + DbSchemaM.ObservancesTable.Cols.short_name + ", "
            + DbSchemaM.ObservancesTable.Cols.sutra_text
            + ") VALUES (?, ?)", (i_short_name_sg, i_sutra_text_sg))

    @staticmethod
    def get(i_observance_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.ObservancesTable.name
            + " WHERE " + DbSchemaM.ObservancesTable.Cols.list_pos + "=" + str(i_observance_id_it))
        t_observance_tuple_from_db = db_cursor_result.fetchone()
        db_connection.commit()

        return ObservanceM(t_observance_tuple_from_db[1], t_observance_tuple_from_db[2])

    @staticmethod
    def get_all():
        ret_observance_lt = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute("SELECT * FROM " + DbSchemaM.ObservancesTable.name)
        t_observances_from_db = db_cursor_result.fetchall()
        for t_tuple in t_observances_from_db:
            ret_observance_lt.append(ObservanceM(t_tuple[1], t_tuple[2]))
        db_connection.commit()

        return ret_observance_lt


class KarmaM:
    def __init__(self, i_observance_ref_it, i_pos_it, i_description_sg):
        self.observance_ref_it = i_observance_ref_it
        self.pos_it = i_pos_it
        self.description_sg = i_description_sg

    @staticmethod
    def add(i_observance_ref_id_it, i_pos_it, i_description_sg):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.KarmaTable.name + "("
            + DbSchemaM.KarmaTable.Cols.observance_id + ", "
            + DbSchemaM.KarmaTable.Cols.list_pos + ", "
            + DbSchemaM.KarmaTable.Cols.description
            + ") VALUES (?, ?, ?)", (i_observance_ref_id_it, i_pos_it, i_description_sg)
        )
        db_connection.commit()

    @staticmethod
    def get_all_for_observance(i_observance_id_it):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.KarmaTable.name
            + " WHERE " + DbSchemaM.KarmaTable.Cols.observance_id + "=" + str(i_observance_id_it))
        t_karma_tuple_list_from_db = db_cursor_result.fetchall()
        db_connection.commit()

        karma_list_lt = []
        for karma_db_item in t_karma_tuple_list_from_db:
            karma_list_lt.append(KarmaM(karma_db_item[0], karma_db_item[1], karma_db_item[2]))

        return karma_list_lt

    @staticmethod
    def get_for_observance_and_pos(i_observance_id_it, i_karma_pos_it):
        if i_karma_pos_it == -1:
            return None

        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + DbSchemaM.KarmaTable.name
            + " WHERE " + DbSchemaM.KarmaTable.Cols.observance_id + "=" + str(i_observance_id_it)
            + " AND " + DbSchemaM.KarmaTable.Cols.list_pos + "=" + str(i_karma_pos_it)
        )
        t_karma_tuple_from_db = db_cursor_result.fetchone()
        db_connection.commit()

        return KarmaM(t_karma_tuple_from_db[0], t_karma_tuple_from_db[1], t_karma_tuple_from_db[2])
        #TODO (low prio): Handle "data error" when one of the three has "nonetype"


class DiaryM:
    def __init__(self, i_date_added_it, i_observance_ref, i_karma_ref = -1, i_notes_sg = ""):
        self.date_added_it = i_date_added_it
        self.notes_sg = i_notes_sg
        self.observance_ref = i_observance_ref
        self.karma_ref = i_karma_ref

    @staticmethod
    def add(i_date_added_it, i_observance_ref_id_it, i_karma_ref_id_it, i_notes_sg):
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO " + DbSchemaM.DiaryTable.name + "("
            + DbSchemaM.DiaryTable.Cols.date_added + ", "
            + DbSchemaM.DiaryTable.Cols.observance_id + ", "
            + DbSchemaM.DiaryTable.Cols.karma_id + ", "
            + DbSchemaM.DiaryTable.Cols.notes
            + ") VALUES (?, ?, ?, ?)",
            (i_date_added_it, i_observance_ref_id_it, i_karma_ref_id_it, i_notes_sg)
        )
        db_connection.commit()

    @staticmethod
    def get_all(i_reverse_bl = True):
        ret_diary_lt = []
        db_connection = DbHelperM.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute("SELECT * FROM " + DbSchemaM.DiaryTable.name)
        t_diary_from_db = db_cursor_result.fetchall()
        for t_tuple in t_diary_from_db:
            ret_diary_lt.append(DiaryM(t_tuple[0], t_tuple[1], t_tuple[2], t_tuple[3]))
        db_connection.commit()

        if i_reverse_bl:
            ret_diary_lt.reverse()

        return ret_diary_lt

def export_all():
    csv_writer = csv.writer(open("export.csv", "w"))

    t_space_tab_sg = "    "

    for obs_item in ObservanceM.get_all():
        csv_writer.writerow((obs_item.short_name_sg, obs_item.sutra_text_sg))

    csv_writer.writerow(("\n\n\n",))

    for index in range(0, len(ObservanceM.get_all())):
        csv_writer.writerow((ObservanceM.get(index).short_name_sg,))
        for karma_item in KarmaM.get_all_for_observance(index):
            csv_writer.writerow((t_space_tab_sg + karma_item.description_sg,))

    csv_writer.writerow(("\n\n\n",))

    for diary_item in DiaryM.get_all():
        t_diary_entry_obs_sg = ObservanceM.get(diary_item.observance_ref).short_name_sg
        t_karma = KarmaM.get_for_observance_and_pos(
            diary_item.observance_ref, diary_item.karma_ref)
        if t_karma == None:
            t_diary_entry_karma_sg = ""
        else:
            t_diary_entry_karma_sg = t_karma.description_sg

        csv_writer.writerow((t_diary_entry_obs_sg, t_diary_entry_karma_sg, diary_item.notes_sg))


