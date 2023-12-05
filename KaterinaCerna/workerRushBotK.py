from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId

class workerRushBotK(BotAI):
    NAME: str = "WorkerRushBotK"
    RACE: Race = Race.Terran

    async def on_step(self, iteration: int):
        await self.build_workers()
        await self.build_supply_depots()
        await self.build_refineries()
        await self.build_barracks()
        await self.build_factory()
        await self.train_marines()
        await self.train_marauders()
        await self.train_reapers()
        await self.train_stalkers()
        await self.train_tanks()
        await self.train_hellions()
        await self.train_vikings()
        await self.train_medivacs()
        await self.attack()

    async def build_workers(self):
        if self.townhalls.ready:
            command_center = self.townhalls.ready.random
            if (
                self.can_afford(UnitTypeId.SCV)
                and self.supply_workers <= 16
                and command_center.is_idle
            ):
                command_center.train(UnitTypeId.SCV)

    async def build_supply_depots(self):
        if (
            self.supply_left < 6
            and self.supply_used >= 14
            and not self.already_pending(UnitTypeId.SUPPLYDEPOT)
        ):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                command_center = self.townhalls.ready.random
                await self.build(
                    UnitTypeId.SUPPLYDEPOT,
                    near=command_center.position.towards(
                        self.game_info.map_center, 8
                    ),
                )

    async def build_refineries(self):
        if (
            self.townhalls
            and self.townhalls.ready
            and self.tech_requirement_progress(UnitTypeId.REFINERY) == 1
        ):
            if (
                self.structures(UnitTypeId.REFINERY).amount < 2
                and not self.already_pending(UnitTypeId.REFINERY)
            ):
                command_center = self.townhalls.ready.random
                vespene_geyser = self.vespene_geyser.closest_to(command_center)
                if self.can_afford(UnitTypeId.REFINERY):
                    await self.build(
                        UnitTypeId.REFINERY, near=vespene_geyser, placement_step=1
                    )

    async def build_barracks(self):
        if (
            self.tech_requirement_progress(UnitTypeId.BARRACKS) == 1
            and self.structures(UnitTypeId.BARRACKS).amount < 6
        ):
            command_center = self.townhalls.ready.random
            if (
                self.can_afford(UnitTypeId.BARRACKS)
                and not self.already_pending(UnitTypeId.BARRACKS)
            ):
                await self.build(
                    UnitTypeId.BARRACKS,
                    near=command_center.position.towards(
                        self.game_info.map_center, 8
                    ),
                )
                print("Barracks under construction!")

        if self.tech_requirement_progress(UnitTypeId.BARRACKSTECHLAB) == 1:
            idle_barracks = self.structures(UnitTypeId.BARRACKS).ready.idle
            for barracks in idle_barracks:
                if barracks.add_on_tag == 0:
                    # Kontrola, zda si můžete dovolit stavbu Tech Labu
                    if self.can_afford(UnitTypeId.BARRACKSTECHLAB):
                        barracks.build(UnitTypeId.BARRACKSTECHLAB)
                        print("Tech Lab under construction on Barracks")
                        break

            else:
                if (
                    self.can_afford(UnitTypeId.BARRACKS)
                    and not self.already_pending(UnitTypeId.BARRACKS)
                ):
                    await self.build(
                        UnitTypeId.BARRACKS,
                        near=command_center.position.towards(
                            self.game_info.map_center, 8
                        ),
                    )
                    print("Barracks under construction!")


    async def build_factory(self):
        if (
            self.tech_requirement_progress(UnitTypeId.FACTORY) == 1
            and self.structures(UnitTypeId.FACTORY).amount < 3
        ):
            command_center = self.townhalls.ready.random
            if (
                self.can_afford(UnitTypeId.FACTORY)
                and not self.already_pending(UnitTypeId.FACTORY)
            ):
                await self.build(
                    UnitTypeId.FACTORY,
                    near=command_center.position.towards(
                        self.game_info.map_center, 8
                    ),
                )
                print("Factory under construction!")

    async def train_marines(self):
        if (
            self.structures(UnitTypeId.BARRACKS)
            and self.can_afford(UnitTypeId.MARINE)
        ):
            for barrack in self.structures(UnitTypeId.BARRACKS).idle:
                barrack.train(UnitTypeId.MARINE)

    async def train_marauders(self):
        if (
            self.structures(UnitTypeId.BARRACKS)
            and self.can_afford(UnitTypeId.MARAUDER)
        ):
            for barracks in self.structures(UnitTypeId.BARRACKS).idle:
                barracks.train(UnitTypeId.MARAUDER)

    async def train_reapers(self):
        if (
            self.structures(UnitTypeId.BARRACKS)
            and self.can_afford(UnitTypeId.REAPER)
        ):
            for barracks in self.structures(UnitTypeId.BARRACKS).idle:
                barracks.train(UnitTypeId.REAPER)

    async def train_stalkers(self):
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.can_afford(UnitTypeId.STALKER)
        ):
            for gateway in self.structures(UnitTypeId.GATEWAY).ready.idle:
                gateway.train(UnitTypeId.STALKER)

    async def train_tanks(self):
        if (
            self.structures(UnitTypeId.FACTORY).ready
            and self.can_afford(UnitTypeId.SIEGETANK)
        ):
            for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
                factory.train(UnitTypeId.SIEGETANK)

    async def train_hellions(self):
        if (
            self.structures(UnitTypeId.FACTORY).ready
            and self.can_afford(UnitTypeId.HELLION)
        ):
            for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
                factory.train(UnitTypeId.HELLION)

    async def train_vikings(self):
        if self.structures(UnitTypeId.STARPORT).ready:
            if self.can_afford(UnitTypeId.VIKING):
                for starport in self.structures(UnitTypeId.STARPORT).ready.idle:
                    starport.train(UnitTypeId.VIKING)

    async def train_medivacs(self):
        if self.structures(UnitTypeId.STARPORT).ready:
            for starport in self.structures(UnitTypeId.STARPORT).ready.idle:
                if (
                    starport.add_on_tag in self.state.tags
                    and self.can_afford(UnitTypeId.MEDIVAC)
                    and starport.is_idle
                ):
                    starport.train(UnitTypeId.MEDIVAC)
                    print("Training Medivac!")
                elif starport.add_on_tag not in self.state.tags:
                    print("Starport does not have Tech Lab!")
                elif not self.can_afford(UnitTypeId.MEDIVAC):
                    print("Not enough resources to train Medivac!")
                elif not starport.is_idle:
                    print("Starport is not idle!")
                else:
                    print("Conditions for training Medivac not met!")

    async def attack(self):
        idle_marines = self.units(UnitTypeId.MARINE).idle
        if idle_marines.amount > 15:
            target = self.enemy_structures.random_or(
                self.enemy_start_locations[0]
            ).position
            for marine in idle_marines:
                marine.attack(target)
                print(f"Marine attacking {target}")

        idle_marauders = self.units(UnitTypeId.MARAUDER).idle
        if idle_marauders.amount > 5:
            target = self.enemy_structures.random_or(
                self.enemy_start_locations[0]
            ).position
            for marauder in idle_marauders:
                marauder.attack(target)
                print(f"Marauder attacking {target}")

        # Přidání Siege Tanků do útoku
        idle_siege_tanks = self.units(UnitTypeId.SIEGETANK).idle
        if idle_siege_tanks.amount > 0:
            target = self.enemy_structures.random_or(
                self.enemy_start_locations[0]
            ).position
            for siege_tank in idle_siege_tanks:
                siege_tank.attack(target)
                print(f"Siege Tank attacking {target}")

        idle_hellions = self.units(UnitTypeId.HELLION).idle
        if idle_hellions.amount > 0:
            target = self.enemy_structures.random_or(
                self.enemy_start_locations[0]
            ).position
            for hellion in idle_hellions:
                hellion.attack(target)
                print(f"Hellion attacking {target}")

run_game(maps.get("sc2-ai-cup-2022"), [
    Bot(Race.Terran, workerRushBotK()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=False)
