from enum import Enum
from typing import Any, Optional

from fastapi import HTTPException


class ErrorCode(Enum):
    """
    B0000 = Rocket backend error
    F0000 = Rocket frontend error
    U0000 = User error
    P0000 = Profit error
    Z0000 = Other error
    """

    B0000 = "Onbekende backend error opgetreden"
    B0001 = "Verkeerd aantal msg args meegegeven, verwacht: %s ontvangen: %s"
    B0002 = "Parameter niet meegegeven in de JSON. Contact de developers en maak een screenshot van de error."
    B0003 = "Method_id niet meegegeven of verander in de JSON. Contact de developers en maak een screenshot van de " \
            "error."
    B0004 = "Label en/of Id is niet bekend of niet aanwezig in de source_data."
    B0005 = "Tijdens het genereren ontstaat er een error door de Hierarchy."
    B0006 = "Tijdens het berekenen van het aantal rijen is er een error gekomen."
    B0007 = "De gegeven verzendmethode is niet bekend in het systeem. Contact de developers en maak een screenshot " \
            "van de error."
    B0008 = "Het gegeven fieldId is niet beschikbaar in de metainfo. Contact de developers en maak een screenshot " \
            "van de error."
    B0009 = "Method_id is niet gevonden in de metatinfo. Contact de developers en maak een screenshot van de error."
    B0010 = "Bij veld: %s; en dan functie: %s; zijn geen functies meegegeven."
    B0011 = "Bij veld %s; Functie: %s; Parameter: %s; zijn geen functies of waardes gedefiniëerd."
    B0012 = "De GetConnector bij Bron Percentage wordt niet meegegeven in de JSON. Contact de developers en maak een" \
            " screenshot van de error."
    B0013 = "Work in progress."
    B0014 = "Process heeft al een entity, gebruik het andere endpoint Finn!!"
    B0015 = "Bij het verwijderen van lege regels gaat het niet goed. Het eerste item is een lijst en dat klopt niet."

    F0000 = "Onbekende frontend error opgetreden"
    F0001 = "Sourcetype is een CSV en die wordt nog niet ondersteunt."
    F0002 = "Geen functies in het huidige of geïnherite process. Contact de developers en maak een screenshot " \
            "van de error."
    F0003 = "Bij veld: %s; zijn geen functies meegegeven."
    F0004 = "Bij het aanmaken van een process of notitie wordt in de JSON van de entity geen process en notitie " \
            "meegegeven."
    F0005 = "Bij het aanmaken van een process of notitie worden beide items meegegeven. Dit kan niet. Contact de " \
            "developers en maak een screenshot van de error."
    F0006 = "Bij het veranderen van de order_ids wordt niet de goede 'type_update' meegegeven. Dit kan alleen " \
            "'chapters' of 'entities' zijn."

    U0000 = "Onbekende User error opgetreden."
    U0001 = "Geen template gevonden met id '%s'"
    U0002 = "Geen process gevonden met id '%s'"
    U0003 = "Geen process gevonden met id: '%s' in het template met id: '%s'"
    U0004 = "U moet eerst een inheritable (basis) template maken."
    U0005 = "U kunt maar maximaal 1 inheritable (basis) template maken."
    U0006 = (
        "U kunt dit process niet verwijderen omdat er nog andere processen dit process inheriten, "
        "verwijder die eerst."
    )
    U0007 = "Geen CSV file gevonden met id '%s'."
    U0008 = "Circulaire afhankelijkheden tussen de velden: '%s'"
    U0009 = "De datum(s) staan niet in het goede formaat. Het goede formaat is: '%s' of '%s'."
    U0010 = "De minimale waarde is hoger dan de maximale waarde."
    U0011 = "Stapgrootte kan niet gelijk zijn aan 0."
    U0012 = "Begin datum is na de eind datum."
    U0013 = "De ingevoerde operator: %s is niet geldig. De gewenste operators zijn: [ =,  <,  <=,  >,  >=]"
    U0014 = "De ingevoerde waarde is geen cijfer."
    U0015 = "De minimale aantal rijen is groter dan de maximale aantal rijen."
    U0016 = "U maakt gebruik van een GetConnector die geen rijen met data bevat. Verwijder deze eerst voordat u " \
            "doorgaat met genereren."
    U0017 = "U vraagt velden op van GetConnector %s maar die staat niet meer bij de bronnen. "
    U0018 = "U gebruikt de functie Random Selectie bij veld %s en die heeft geen waardes uit Profit."
    U0019 = "Aantal rijen is te hoog om de waardes van bron %s uniek te houden. Zet de bronherhaling aan om meer " \
            "waardes te genereren of verlaag het aantal rijen."
    U0020 = "U heeft geen verzendmethode opgegeven. Dit is belangrijk als u de gegenereerde data wilt exporteren. " \
            "Vul een verzendmethode in voor de volgende keer genereren."
    U0021 = "U vraagt van connector %s veld %s op, maar dat die connector en dat veld zijn nog niet gegenereerd, omdat " \
            "die connector lager dan de huidige connector zit. Voor nu " \
            "kunt u alleen velden gebruiken van zelfde connector of van een connector boven je huidige connector."
    U0022 = "U vraagt veld %s op van GetConnector %s, maar dat veld bestaat niet in de GetConnector."
    U0023 = "U hebt geen 1 parameter van de functie Tekst Samenvoegen ingevuld."
    U0024 = "U heeft bij veld %s; functie %s geen 1 parameter ingevuld."
    U0025 = "Geen chapter gevonden met id: '%s' in het template met id: '%s'"
    U0026 = "U kunt hoofdstuk %s niet verwijderen, omdat er nog een process of notitie onderstaat. Verwijder of " \
            "verplaats deze eerst, voordat u het hoofdstuk kunt verwijderen."
    U0027 = "Geen process of notitie gevonden met id %s in template %s."
    U0028 = "Geen notitie gevonden met id %s in template %s"
    U0029 = "Geen notitie item gevonden met id %s bij notitie %s."
    U0030 = "Bij functie Bron waarde met Vaste Waarde heeft u door de filtering van het veld %s nog maar %s aantal " \
            "rijen die mogelijk zijn om te genereren, maar u heeft %s opgegeven. Verlaag het aantal rijen om goed te " \
            "genereren."
    U0031 = "U wilt veld %s gebruiken in veld %s. Dit kan natuurlijk niet. Gebruik een ander veld."

    P0000 = "Onbekende profit error opgetreden"
    P0001 = "Kan geen connectie maken naar profit met de gegeven endpoint en token"
    P0002 = "Toegang geblokkeerd, u heeft hier geen toegang toe."
    P0003 = "Certificaat error. Controleer of het certificaat nog voldoet aan de gestelde eisen."
    P0004 = "De gestuurde request is gestuit op restricties. Neem contact op met de developers voor meer informatie."
    P0005 = "De opgevraagde data overtreed de SSL(Secure Sockets Layer)."
    P0006 = "De Request is geblokeerd door restricties die specifiek gelden voor u als gebruiker."
    P0007 = "Er ontbreken specifieke authenticatie codes voor deze Proxy verbinding."
    P0008 = "Uw Windows/MacOS/Linux blokkeert en geeft errors. Probeer het nog eens op een andere laptop met een " \
            "ander besturingssysteem."
    P0009 = "De ontvangen data is niet in het goede format(JSON) en kan niet worden uitgelezen. " \
            "Neem contact op met de developers."
    P0010 = "De ingevoerde URL bestaat niet."
    P0011 = "Momenteel is de pagina niet beschikbaar, omdat er geen connectie gemaakt kan worden met de server. " \
            "Check https://afasstatus.nl/ voor meer informatie."
    P0012 = "Server geeft een timeout. Verlaag het aantal requests of neem contact op met de developers."
    P0013 = "In dit process staat Getconnector %s en die staat niet in de App Connector in profit. Voeg deze eerst " \
            "toe voordat u iets kunt doen."

    Z0000 = "Onbekende error opgetreden"


class RocketError(Exception):
    def __init__(
            self,
            error_code: ErrorCode,
            msg_args: tuple = (),
            status_code: Optional[int] = None,
            **kwargs: Any,
    ):
        if (formats := error_code.value.count("%s")) != len(msg_args):
            raise HTTPException(500, ErrorCode.B0001.value % (formats, len(msg_args)))
        self.error_code = error_code
        self.msg_args = msg_args
        self.error_msg = error_code.value % msg_args
        self.status_code = status_code
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"({self.error_code.name}) {self.error_msg}"


class ProfitError(RocketError):
    pass


class DatabaseError(RocketError):
    pass


class GeneratorError(RocketError):
    pass


if __name__ == "__main__":
    print(issubclass(RocketError, RocketError))
