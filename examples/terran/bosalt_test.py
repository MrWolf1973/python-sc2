import random

import sc2
from sc2 import Race, Difficulty, BoSALT
from sc2.constants import *
from sc2.ids.buff_id import BuffId
from sc2.player import Bot, Computer

class BoSALT_Test(sc2.BotAI):
    def __init__(self):
        self.bosalt = BoSALT()
        salt = "$49773|spawningtool.com||~* 1 /+ H !, K ,/!;\" /!= )/!J #0\"  !0\"%!%2\"-!%2\"/ /3\"; !3\"C!%3\"C!%6\"Q 07\"W\" 7\"[!%7\"[!%:#(!%:#(#+;#/ );#1!%;#1!%>#7 %@#A ,@#D!%E#M /K$* .K$* *[$U!&[$U!&[$Z $a%+#0"
        self.bosalt.set_bo_salt(salt)

    async def on_step(self, iteration):
        if iteration % 100 == 0:
            unit = await self.bosalt.nextbestboaction(game_data=self)
            await self.chat_send("(probe)(pylon)(cannon)(cannon)(gg)" + str(iteration) + ":" + str(unit))
            await self.managebuild(unit)
        await self.distribute_workers()

    async def managebuild(self, unit):
        if unit == SCV:
            for cc in ((self.units(ORBITALCOMMAND).ready | self.units(COMMANDCENTER).ready  | self.units(ORBITALCOMMAND).ready)):
                if len(cc.orders) < 2 and self.can_afford(SCV):
                    await self.do(cc.train(SCV))
                    break
        elif unit in (SUPPLYDEPOT, BARRACKS, COMMANDCENTER, FACTORY, STARPORT, REFINERY): #building
            if self.can_afford(unit):
                if unit == REFINERY:
                    for cc in (self.units(ORBITALCOMMAND).ready | self.units(COMMANDCENTER).ready | self.units(ORBITALCOMMAND).ready):
                        for vespingayser in (self.state.vespene_geyser.closer_than(10.0, cc)):
                            if not self.units(REFINERY).closer_than(1.0, vespingayser).exists and self.can_afford(REFINERY):
                                worker = self.select_build_worker(vespingayser.position)
                                await self.do(worker.build(REFINERY, vespingayser))
                                break
                else:
                    location = self.start_location.towards(self.game_info.map_center, 8)
                    await self.build(unit, near=location)
        elif unit == ORBITALCOMMAND:
            for cc in (self.units(ORBITALCOMMAND).ready):
                self.combinedActions.append(cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))



def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, BoSALT_Test()),
        Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
    main()




