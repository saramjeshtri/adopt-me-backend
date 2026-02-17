from enum import Enum

# LLOJET E RAPORTIT (Report Types)
class LlojiRaportit(str, Enum):
    abuzim       = "Abuzim me kafshë"
    e_humbur     = "Kafshë e humbur"
    agresive     = "Kafshë agresive"
    e_lenduar    = "Kafshë e lënduar"
    braktisje    = "Braktisje kafshësh"
    tjetër       = "Tjetër"

# STATUSI I RAPORTIT (Report Status)
class StatusiRaportit(str, Enum):
    hapur           = "Hapur"
    ne_process      = "Në proces"
    zgjidhur_gjetur = "Zgjidhur - Kafshë e gjetur"
    zgjidhur_jo     = "Zgjidhur - Nuk u gjet"
    kthyer_pronarit = "Zgjidhur - Kthyer pronarit"

# LLOJET E KAFSHËVE (Animal Species)
class LlojiKafshes(str, Enum):
    qen     = "Qen"
    mace    = "Mace"
    zog     = "Zog"
    kalë    = "Kalë"
    tjetër  = "Tjetër"

# GJINIA E KAFSHËS (Animal Gender)
class GjiniaKafshes(str, Enum):
    mashkull = "Mashkull"
    femër    = "Femër"
    e_panjohur = "E panjohur"

# STATUSI I ADOPTIMIT (Adoption Status)
class StatusiAdoptimit(str, Enum):
    disponueshme  = "Disponueshme"
    takim_planifikuar = "Takim i planifikuar"
    adoptuar      = "Adoptuar"
    jo_disponueshme = "Jo disponueshme"

# STATUSI I SHËNDETIT (Health Status)
class StatusiShendetit(str, Enum):
    shendetshem  = "Shëndetshëm"
    i_lenduar    = "I lënduar"
    ne_trajtim   = "Në trajtim"
    ne_rikuperim = "Në rikuperim"

# STATUSI I TAKIMIT (Meeting Status)
class StatusiTakimit(str, Enum):
    ne_pritje   = "Në pritje"
    konfirmuar  = "Konfirmuar"
    perfunduar  = "Përfunduar"
    anulluar    = "Anulluar"

# LLOJET E MEDIAVE (Media Types)
class LlojiMedias(str, Enum):
    foto  = "foto"
    video = "video"

# DEPARTMENT ROUTING MAP
ROUTING_DEPARTAMENTIT = {
    LlojiRaportit.abuzim:       "Shërbimi Veterinar",
    LlojiRaportit.e_humbur:     "Policia Bashkiake",
    LlojiRaportit.agresive:     "Policia Bashkiake",
    LlojiRaportit.e_lenduar:    "Shërbimi Veterinar",
    LlojiRaportit.braktisje:    "Sektori i Mjedisit",
    LlojiRaportit.tjetër:       "Shërbimi Veterinar",  
}

HEALTH_NE_ADOPTIM = {
    StatusiShendetit.shendetshem:  StatusiAdoptimit.disponueshme,
    StatusiShendetit.i_lenduar:    StatusiAdoptimit.jo_disponueshme,
    StatusiShendetit.ne_trajtim:   StatusiAdoptimit.jo_disponueshme,
}