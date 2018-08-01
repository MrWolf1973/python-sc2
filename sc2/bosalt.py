from datetime import datetime
import sc2
from sc2.constants import *


class BoSALT(object):
    def __init__(self):
        dummy = -1
        self.build_order = {}
        self.CHARACTERS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        self.structure = ARMORY, BARRACKS, BUNKER, COMMANDCENTER, ENGINEERINGBAY, FACTORY, FUSIONCORE, GHOSTACADEMY, MISSILETURRET, BARRACKSREACTOR, \
            FACTORYREACTOR, STARPORTREACTOR, REFINERY, SENSORTOWER, STARPORT, SUPPLYDEPOT, BARRACKSTECHLAB, FACTORYTECHLAB, \
            STARPORTTECHLAB, \
            ASSIMILATOR, CYBERNETICSCORE, DARKSHRINE, FLEETBEACON, FORGE, GATEWAY, NEXUS, PHOTONCANNON, PYLON, \
            ROBOTICSBAY, ROBOTICSFACILITY, STARGATE, TEMPLARARCHIVE, TWILIGHTCOUNCIL, \
            BANELINGNEST, EVOLUTIONCHAMBER, EXTRACTOR, HATCHERY, HYDRALISKDEN, INFESTATIONPIT, NYDUSNETWORK, ROACHWARREN, \
            SPAWNINGPOOL, SPINECRAWLER, SPIRE, SPORECRAWLER, ULTRALISKCAVERN, CREEPTUMOR
        self.unit = BANSHEE, BATTLECRUISER, GHOST, HELLION, MARAUDER, MARINE, MEDIVAC, RAVEN, REAPER, SCV, SIEGETANK, THOR, dummy, VIKINGASSAULT, CARRIER, COLOSSUS, \
            DARKTEMPLAR, HIGHTEMPLAR, IMMORTAL, MOTHERSHIP, OBSERVER, PHOENIX, PROBE, SENTRY, STALKER, VOIDRAY, ZEALOT, CORRUPTOR, DRONE, \
            HYDRALISK, MUTALISK, OVERLORD, QUEEN, ROACH, ULTRALISK, ZERGLING, INFESTOR, WARPPRISM, HELLION, WARHOUND, WIDOWMINE, \
            MOTHERSHIPCORE, ORACLE, TEMPEST, SWARMHOSTMP, VIPER, CYCLONE, LIBERATOR, DISRUPTOR, ADEPT
        self.morph = ORBITALCOMMAND, PLANETARYFORTRESS, WARPGATE, LAIR, HIVE, GREATERSPIRE, BROODLORD, BANELING, OVERSEER, RAVAGER, LURKER, dummy, LURKERDEN, ARCHON
        self.upgrade = TERRANBUILDINGARMOR, TERRANINFANTRYARMORSVANADIUMPLATINGLEVEL1, TERRANINFANTRYWEAPONSLEVEL1, TERRANSHIPARMORSVANADIUMPLATINGLEVEL1, \
            TERRANSHIPWEAPONSLEVEL1, TERRANVEHICLEARMORSVANADIUMPLATINGLEVEL1, TERRANVEHICLEWEAPONSLEVEL1, STRIKECANNONS, \
            BANSHEECLOAK, PERSONALCLOAKING, HELLIONCAMPAIGNINFERNALPREIGNITER, STIMPACK, \
            HUNTERSEEKER, SIEGETECH, NEOSTEELFRAME, MARAUDERLIFEBOOST, \
            COMBATSHIELD, REAPERSPEED, PROTOSSGROUNDARMORSLEVEL1, PROTOSSGROUNDWEAPONSLEVEL1, \
            PROTOSSAIRARMORSLEVEL1, PROTOSSAIRWEAPONSLEVEL1, PROTOSSSHIELDSLEVEL1, dummy, \
            PSISTORMTECH, BLINKTECH, WARPGATERESEARCH, CHARGE, \
            ZERGGROUNDARMORSLEVEL1, ZERGMELEEWEAPONSLEVEL1, ZERGFLYERARMORSLEVEL1, ZERGFLYERWEAPONSLEVEL1, \
            ZERGMISSILEWEAPONSLEVEL1, EVOLVEGROOVEDSPINES, ORGANICCARAPACE, OVERLORDTRANSPORT, \
            GLIALRECONSTITUTION, dummy, TUNNELINGCLAWS, dummy, CHITINOUSPLATING, \
            ZERGLINGATTACKSPEED, ZERGLINGMOVEMENTSPEED, dummy, BURROW, \
            CENTRIFICALHOOKS, GHOSTMOEBIUSREACTOR, EXTENDEDTHERMALLANCE, dummy, \
            NEURALPARASITE, INFESTORENERGYUPGRADE, BATTLECRUISERBEHEMOTHREACTOR, YAMATOCANNON, \
            HISECAUTOTRACKING, MEDIVACCADUCEUSREACTOR, RAVENCORVIDREACTOR, DURABLEMATERIALS, \
            TRANSFORMATIONSERVOS, GRAVITICTHRUSTERS, OBSERVERGRAVITICBOOSTER, GRAVITICDRIVE, \
            dummy, dummy, dummy, dummy, \
            EVOLVEMUSCULARAUGMENTS, DRILLCLAWS, ANIONPULSECRYSTALS, FLYINGLOCUSTS, \
            EVOLVEGROOVEDSPINES, dummy, CYCLONELOCKONRANGEUPGRADE, LIBERATORAGRANGEUPGRADE, \
            ADEPTPIERCINGATTACK

    def set_bo_salt(self, salt):
        bo = salt[salt.find("~")+1:]

        for step in (bo[i:5+i] for i in range(0,len(bo)-1, 5)):
            if len(step) == 5:
                supply = "S" + str(self.CHARACTERS.find(step[0]) + 4)
                ingametime = datetime.strptime(str(self.CHARACTERS.find(step[1])) + ':' + str(self.CHARACTERS.find(step[2])), '%M:%S')
                typ = self.CHARACTERS.find(step[3])
                code = self.CHARACTERS.find(step[4])
                bo_task = self.transcode(typ, code)

                if len(self.build_order) > 0:
                    build_step = self.build_order[list(self.build_order.keys())[-1]].copy()
                else:
                    build_step = {}

                if bo_task in build_step:
                    build_step[bo_task] = build_step[bo_task] + 1
                else:
                    build_step[bo_task] = 1
                self.build_order[supply] = build_step

    def transcode(self, typ, code):
        if typ == 0:  # Structure
            bo_id = self.structure[int(code)]
        elif typ == 1:  # Unit
            bo_id = self.unit[int(code)]
        elif typ == 2:  # Morph
            bo_id = self.morph[int(code)]
        elif typ == 3:  # Upgrade
            bo_id = self.upgrade[int(code)]
        return bo_id

    async def nextbestboaction(self, game_data):
        laststep = self.laststep(game_data.supply_used)
        for unittyp in laststep.keys():
            target = int(laststep[unittyp])
            if type(unittyp) == UpgradeId:
                pending = 0
                ready = 0
            else:
                ready = game_data.units(unittyp).amount
                pending = game_data.already_pending(unittyp)

            if unittyp == COMMANDCENTER:
                morphingout = game_data.already_pending(ORBITALCOMMAND) + game_data.already_pending(PLANETARYFORTRESS)
            else:
                morphingout = 0

            if target > (pending + ready - morphingout):
                return unittyp

        if "S" + str(game_data.supply_used) in self.build_order.keys():
            actstep = self.build_order["S" + str(game_data.supply_used)]
        else:
            actstep = {}
        for unittyp in actstep.keys():
            target = int(actstep[unittyp])
            if type(unittyp) == UpgradeId:
                pending = 0
                ready = 0
            else:
                ready = game_data.units(unittyp).amount
                pending = game_data.already_pending(unittyp)

            if unittyp == COMMANDCENTER:
                morphingout = game_data.already_pending(ORBITALCOMMAND) + game_data.already_pending(PLANETARYFORTRESS)
            else:
                morphingout = 0

            if target > (pending + ready - morphingout):
                return unittyp


        return SCV


    def laststep(self, supply) -> dict:
        presupply = 0

        for prekey in (int(key[1:]) for key in self.build_order.keys()):
            if prekey < supply and prekey > presupply:
                presupply = prekey
        if presupply > 0:
            return self.build_order["S" + str(presupply)]
        else:
            return {}

def main():
    test = BoSALT()
    salt = "$49773|spawningtool.com||~* 1 /+ H !, K ,/!;\" /!= )/!J #0\"  !0\"%!%2\"-!%2\"/ /3\"; !3\"C!%3\"C!%6\"Q 07\"W\" 7\"[!%7\"[!%:#(!%:#(#+;#/ );#1!%;#1!%>#7 %@#A ,@#D!%E#M /K$* .K$* *[$U!&[$U!&[$Z $a%+#0"
    test.set_bo_salt(salt)
    print(test.build_order)

if __name__ == '__main__':
    main()
