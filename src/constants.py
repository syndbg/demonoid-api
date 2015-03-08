import sys

if sys.version_info >= (3, 0):
    class_type = type
else:
    from new import classobj
    class_type = classobj


__all__ = ['SortBy', 'Category', 'Quality', 'Language', 'State', 'TrackedBy']


# Borrowed from https://github.com/karan/TPB and modified.
# Props to Karan.
class ConstantType(type):

    """
    Tree representation metaclass for class attributes. Metaclass is extended
    to all child classes too.
    """
    def __new__(cls, clsname, bases, dct):
        """
        Extend metaclass to all class attributes too.
        """
        attrs = {}
        for name, attr in dct.items():
            if isinstance(attr, class_type):
                # substitute attr with a new class with Constants as
                # metaclass making it possible to spread this same method
                # to all child classes
                attr = ConstantType(
                    attr.__name__, attr.__bases__, attr.__dict__)
            attrs[name] = attr
        return super(ConstantType, cls).__new__(cls, clsname, bases, attrs)

    def __repr__(cls):
        """
        Tree representation of class attributes. Child classes are also
        represented.
        """
        str_representation = '{0}: {1}\n'.format(cls.__name__, cls.value)
        for name in dir(cls):
            if not name.startswith('_'):
                attr = getattr(cls, name)
                output = repr(attr)
                if not isinstance(attr, ConstantType):
                    output = '{0}: {1}'.format(name, output)
                # indent all child attrs
                str_representation += '\n'.join([' ' * 4 + line
                                                 for line in output.splitlines()]) + '\n'
        return str_representation

    def __str__(cls):
        return repr(cls)

    @property
    def value(cls):
        try:
            return cls.__value__
        except:
            return None

    @property
    def is_child(cls):
        return cls.value is None


Constants = ConstantType('Constants', (object,), {})
# END OF COPIED


class SortBy(Constants):
    DATE = ''  # default

    class COMPLETED:
        ASCENDING = 'c'
        DESCENDING = 'C'

    class LEECHERS:
        ASCENDING = 'l'
        DESCENDING = 'L'

    class SEEDERS:
        ASCENDING = 's'
        DESCENDING = 'S'

    class SIZE:
        ASCENDING = 'b'
        DESCENDING = 'B'


class Category(Constants):

    class ALL:
        __value__ = 0
        ALL = 0

    class APPLICATIONS:
        __value__ = 5
        ALL = 0
        ANDROID = 284
        IOS = 277  # original Iphone / Ipod touch
        LINUX = 2
        MAC = 3
        MOBILE_PHONE = 118
        PALM = 5
        POCKET_PC = 4
        WINDOWS = 1

    class AUDIO_BOOKS:
        __value__ = 17
        ALL = 0
        ACTION = 140
        ADVENTURE = 139
        BIOGRAPHY = 301
        CHILDRENS = 142
        COMPUTERS_AND_TECHNOLOGY = 157
        CONTEMPORARY = 143
        COOKING = 315
        CRAFTS_AND_HOBBIES = 302
        EDUCATIONAL = 158
        EDUCATIONAL2 = 303  # duplicate in their filters. No idea what's for yet.
        FANTASY = 144
        FICTION = 304
        GENERAL = 145
        HISTORY = 305
        HORROR = 146
        HUMOR = 147
        LITERARY = 148
        MAGAZINE = 307
        MAINSTREAM = 149
        MEDICINE_AND_HEALTH = 308
        MYSTERY_AND_SUSPENSE = 150
        NEWSPAPER = 309
        NONFICTION = 310
        OTHER = 231
        PARANORMAL = 151
        RELIGION = 311
        ROMANCE = 152
        RPG = 312
        SCI_FI = 153
        SELF_HELP = 141
        SUSPENSE = 154
        TEXTBOOK = 313
        THRILLER = 155
        WESTERN = 156
        YOUNG_ADULT = 314

    class BOOKS:
        __value__ = 11
        ALL = 0
        ACTION_AND_ADVENTURE = 119
        BIOGRAPHY = 288
        CHILDRENS = 122
        COMPUTERS_AND_TECHNOLOGY = 137
        CONTEMPORARY = 123
        COOKING = 316
        CRAFTS_AND_HOBBIES = 289
        EDUCATIONAL = 138
        FANTASY = 124
        FICTION = 291
        GENERAL = 125
        HISTORY = 293
        HORROR = 126
        HUMOR = 127
        LITERARY = 128
        MAGAZINE = 263
        MAINSTREAM = 129
        MEDICINE_AND_HEALTH = 295
        MYSTERY_AND_SUSPENSE = 130
        NEWSPAPER = 264
        NONFICTION = 297
        OTHER = 230
        PARANORMAL = 131
        RELIGION = 298
        ROMANCE = 132
        RPG = 260
        SCI_FI = 133
        SELF_HELP = 121
        SUSPENSE = 134
        TEXTBOOK = 299
        THRILLER = 135
        WESTERN = 136
        YOUNG_ADULT = 300

    class COMICS:
        __value__ = 10
        ALL = 0
        ACTION_AND_ADVENTURE = 159  # Action/Adventure in site, but here it's kept for consistency with Books.ACTION_AND_ADVENTURE
        CRIME = 227
        DRAMA = 160
        FANTASY = 223
        HISTORICAL_FICTION = 228
        HORROR = 224
        ILLUSTRATED_NOVEL = 161
        MANGA = 285
        OTHER = 229
        REAL_LIFE = 226
        SCI_FI = 225
        SUPER_HERO = 222

    class GAMES:
        __value__ = 4
        ALL = 0
        DOS = 177
        DREAMCAST = 176
        EMULATORS = 178
        GAMEBOY = 167
        GAMECUBE = 175
        LINUX = 162
        MAC = 163
        MOBILE_PHONE = 168
        NINTENDO_DS = 261
        PALM = 164
        PLAYSTATION_1 = 170
        PLAYSTATION_2 = 171
        PLAYSTATION_3 = 172
        POCKET_PC = 165
        PSP = 169
        PSP_PSX = 274
        WII = 271
        WINDOWS = 166
        XBOX = 173
        XBOX_360 = 174

    class JAPANESE_ANIME:
        __value__ = 9
        ALL = 0
        ACTION = 111
        ADVENTURE = 220
        COMEDY = 112
        DRAMA = 113
        FANTASY = 114
        HORROR = 115
        OTHER = 221
        ROMANCE = 117
        SCI_FI = 116

    class MISCELLANEOUS:
        __value__ = 6

    class MOVIES:
        __value__ = 1
        ALL = 0
        ACTION = 6
        ADVENTURE = 7
        ANIMATION = 8
        BIOGRAPHY = 9
        COMEDY = 10
        CONCERTS = 180
        CRIME = 181
        DOCUMENTARY = 11
        DRAMA = 12
        FAMILY = 13
        FANTASY = 14
        FILM_NOIR = 15
        HORROR = 17
        MUSICAL = 18
        MYSTERY = 19
        OTHER = 65
        ROMANCE = 20
        SCI_FI = 21
        SHORT_FILM = 22
        SPORTS = 23
        THRILLER = 24
        TRAILERS = 182
        WAR = 25
        WESTERN = 26

    class MUSIC:
        __value__ = 2
        ALL = 0
        ALTERNATIVE = 183
        BLUEGRASS = 265
        BLUES = 34
        CHILDRENS = 280
        CHRISTIAN = 185
        CLASSICAL = 27
        COMEDY = 186
        CONTEMPORARY_AFRICAN = 44
        COUNTRY = 36
        DANCE_DISCO = 39
        DRUM_AND_BASS = 282
        ELECTRO_TECHNO = 37
        FOLK = 269
        GOSPEL = 28
        GRUNGE = 275
        HIPHOP_RAP = 43
        INDIE = 266
        INDUSTRIAL = 38
        JAZZ = 29
        JPOP = 184
        LATIN_AMERICAN = 30
        MELODIC = 40
        METAL = 35
        OTHER = 63
        POP = 31
        PUNK = 42
        RADIO_SHOW = 286
        REGGAE = 41
        RHYTHM_AND_BLUES = 33
        ROCK = 32
        SOUL = 188
        SOUNDTRACK = 190
        TRANCE = 191
        TRIP_HOP = 278

    class MUSIC_VIDEOS:
        __value__ = 13
        ALL = 0
        ALTERNATIVE = 251
        BLUEGRASS = 268
        BLUES = 239
        CHILDRENS = 281
        CHRISTIAN = 253
        CLASSICAL = 232
        COMEDY = 254
        CONTEMPORARY_AFRICAN = 249
        COUNTRY = 241
        DANCE_DISCO = 244
        DRUM_AND_BASS = 283
        ELECTRO_TECHNO = 242
        FOLK = 270
        GOSPEL = 233
        GRUNGE = 276
        HIPHOP_RAP = 248
        INDIE = 267
        INDUSTRIAL = 243
        JAZZ = 234
        JPOP = 252
        LATIN_AMERICAN = 235
        MELODIC = 245
        METAL = 240
        OTHER = 250
        POP = 236
        PUNK = 247
        REGGAE = 246
        RHYTHM_AND_BLUES = 238
        ROCK = 237
        SOUL = 255
        SOUNDTRACK = 257
        TRANCE = 258
        TRIP_HOP = 279

    class PICTURES:
        __value__ = 8
        ALL = 0
        ART = 66
        COMMERCIAL = 67
        GLAMOUR = 69
        OTHER = 73
        PHOTOJOURNALISM = 68
        SNAPSHOTS = 70
        SPORTS = 71
        WILDLIFE = 72

    class TV:
        __value__ = 3
        ALL = 0
        ACTION = 192
        ADVENTURE = 193
        BIOGRAPHY = 195
        CARTOONS = 194
        COMEDY = 196
        CONCERTS = 213
        CRIME = 214
        DOCUMENTARY = 197
        DRAMA = 198
        FAMILY = 199
        FANTASY = 200
        FILM_NOIR = 201
        HORROR = 203
        MUSICAL = 202
        MYSTERY = 204
        OTHER = 212
        REALITY = 262
        ROMANCE = 205
        SCI_FI = 206
        SHORT_FILM = 207
        SPORTS = 208
        TALK_SHOW = 259
        THRILLER = 209
        TRAILERS = 215
        WAR = 210
        WESTERN = 211


class Language(Constants):
    ALL = 0
    ARABIC = 19
    BULGARIAN = 20
    CHINESE = 12
    CROATIAN = 14
    CZECH = 13
    DANISH = 11
    ENGLISH = 1
    ESTONIAN = 32
    FARSI = 29
    FINNISH = 33
    FRENCH = 3
    GERMAN = 22
    GREEK = 24
    HEBREW = 23
    HINDI = 31
    HUNGARIAN = 15
    ITALIAN = 4


class Quality(Constants):
    ALL = 0

    class AUDIO_BOOKS:
        AAC = 42
        MP3_128KBPS = 50
        MP3_192KBPS = 49
        MP3_256KBPS = 47
        MP3_64KBPS = 51
        MP3_OVER_256KBPS = 44
        MP3_VARIABLE = 48
        MPC = 43
        OGG = 46
        OTHER = 45

    class GAMES:
        FULL_GAME = 28
        GAME_RIP = 29

    class JAPANESE_ANIME:
        DVD = 34
        HD = 70
        IPOD = 56
        OTHER = 36
        PSP = 58
        TV = 33
        VHS = 35

    class MOVIES:
        BLURAY = 72
        BLURAY_3D = 71
        CAM = 3
        DVD_FULL = 11
        DVD_RIP = 9
        HD_1080 = 68
        HD_720P = 66
        IPOD = 53
        KVCD_DVDRIP = 64
        KVCD_OTHER = 65
        OTHER = 23
        PSP = 60
        REMUX = 73
        SCREENER_DVD = 7
        SCREENER_VHS = 6
        TV_RIP = 8
        VCD_SVCD = 21
        VHS_RIP = HD_1080

    class MUSIC:
        AAC = 18
        LOSSLESS = 62
        MP3_128KBPS = 13
        MP3_192KBPS = 14
        MP3_256KBPS = 16
        MP3_64KBPS = 12
        MP3_OVER_256KBPS = 20
        MP3_SURROUND = 67
        MP3_VARIABLE = 15
        MPC = 19
        OGG = 17
        OTHER = 22
        WMA = 63

    class MUSIC_VIDEOS:
        DVD = 40
        IPOD = 57
        OTHER = 41
        PSP = 61
        TV = 38
        VHS = 39

    class PICTURES:
        HIGH_RESOLUTION = 30
        LOW_RESOLUTION = 31
        MIXED = 32

    class TV:
        DVD = 26
        HD = 69
        IPOD = 54
        OTHER = 55
        PSP = 59
        TV = 24
        VHS = 25


class State(Constants):
    BOTH = 2
    SEEDED = 0
    UNSEEDED = 1


class TrackedBy(Constants):
    BOTH = 2
    DEMONOID = 0
    EXTERNAL = 1
