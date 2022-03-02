# coding:utf-8
import package
"""
TABLE users:
    id INT
    data INT
    
123 = image
321 = posteurID
"""


class DataBaseAccess:
    def __init__(self, connexion):
        self.cursor = connexion.cursor()
        self.connexion = connexion

    def _updateimg(self, imgid):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (123, ))
        self.cursor.execute("INSERT INTO users (id, data) VALUES (?, ?)", (123, imgid))
        self.connexion.commit()

    def _showimg(self):
        rawdata = self.cursor.execute("SELECT data FROM users WHERE id = ?", (123,))
        for raw in rawdata:
            if raw[0] is not None:
                return raw[0]
        return 0

    def _updateposteur(self, posteurid):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (321, ))
        self.cursor.execute("INSERT INTO users (id, data) VALUES (?, ?)", (321, posteurid))
        self.connexion.commit()

    def _showposteur(self):
        rawdata = self.cursor.execute("SELECT data FROM users WHERE id = ?", (321,))
        for raw in rawdata:
            if raw[0] is not None:
                return raw[0]
        return 0

    def _showtopgraph(self):
        rawdata = self.cursor.execute("SELECT data FROM users WHERE id = ?", (7191168,))
        for raw in rawdata:
            if raw[0] is not None:
                return raw[0]
        return 0

    def _updatetopgraph(self, topgraphid):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (7191168,))
        self.cursor.execute("INSERT INTO users (id, data) VALUES (?, ?)", (7191168, topgraphid))
        self.connexion.commit()

    def updatescore(self, cibleid, score):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (cibleid,))
        self.cursor.execute("INSERT INTO users (id, data) VALUES (?, ?)", (cibleid, score))
        self.connexion.commit()

    def showscore(self, cibleid):
        rawdata = self.cursor.execute("SELECT data FROM users WHERE id = ?", (cibleid,))
        for raw in rawdata:
            if raw[0] is not None:
                return raw[0]
        self.cursor.execute("DELETE FROM users WHERE id = ?", (cibleid,))
        self.cursor.execute("INSERT INTO users (id, data) VALUES (?, ?)", (cibleid, 0))
        self.connexion.commit()
        return 0

    def showall(self):
        final = {}
        for raw in self.cursor.execute("SELECT * FROM users"):
            if raw[0] == 321:
                final['image'] = raw[1]
            elif raw[0] == 123:
                final['posteur'] = raw[1]
            else:
                final[raw[0]] = raw[1]
        return final

    def leaderboard(self):
        users = {}
        final = []
        for raw in self.cursor.execute("SELECT id, data FROM users"):
            if len(str(raw[0])) > 3 and raw[0] != 7191168: users[raw[0]] = raw[1]
        users = package.dictionairy(users)
        users.reverse()
        for n in range(10):
            try:
                final.append((users[n][0], users[n][1]))
            except IndexError:
                pass
        return final

    def updatesb(self, sbid, stars, jumpurl=None):
        if not jumpurl:
            rawdata = self.cursor.execute("SELECT jumpurl FROM starbotch WHERE id = ?", (sbid,))
            jumpurl = rawdata.fetchall()[0][0]
        self.cursor.execute("DELETE FROM starbotch WHERE id = ?", (sbid,))
        self.cursor.execute("INSERT INTO starbotch (id, jumpurl, stars) VALUES (?, ?, ?)", (sbid, jumpurl, stars))
        self.connexion.commit()

    def showsb(self, sbid):
        rawdata = self.cursor.execute("SELECT jumpurl, stars FROM starbotch WHERE id = ?", (sbid,))
        for raw in rawdata:
            return raw
        return None

    def showallsb(self):
        final = {}
        for raw in self.cursor.execute("SELECT * FROM starbotch"):
            final[raw[2]] = (raw[0], raw[1])
        return final

    posteur = property(_showposteur, _updateposteur)
    image = property(_showimg, _updateimg)
    topgraph = property(_showtopgraph, _updatetopgraph)

    def coclose(self):
        self.connexion.close()
