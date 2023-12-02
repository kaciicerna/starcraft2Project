from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.bot_ai import BotAI, Race
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId

class workerRushBotK(BotAI):
    NAME: str = "MarineRushBotK"
    RACE: Race = Race.Terran

    async def on_step(self, iteration: int):
        # Jestliže mám Command Center
        if self.townhalls:
            # První Command Center
            command_center = self.townhalls[0]
            # Trénování SCV
            # Bot trénuje nová SCV, jestliže je jich méně než 17
            if self.can_afford(UnitTypeId.SCV) and self.supply_workers <= 16 and command_center.is_idle:
                command_center.train(UnitTypeId.SCV)
            # Postav Supply Depot, jestliže zbývá méně než 6 supply a je využito více než 13
            if self.supply_left < 6 and self.supply_used >= 14 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    # Budova bude postavena poblíž Command Center směrem ke středu mapy
                    # SCV pro stavbu bude vybráno automaticky viz dokumentace
                    await self.build(
                        UnitTypeId.SUPPLYDEPOT,
                        near=command_center.position.towards(self.game_info.map_center, 8))

        if self.tech_requirement_progress(UnitTypeId.REFINERY) == 1:
            # If we have less than 2 refineries and none are pending
            if self.structures(UnitTypeId.REFINERY).amount < 2 and not self.already_pending(UnitTypeId.REFINERY):
                # Find a command center
                command_center = self.townhalls.ready.random
                # Find a nearby Vespene Geyser
                vespene_geyser = self.vespene_geyser.closest_to(command_center)
                # Build a refinery near the Vespene Geyser
                if self.can_afford(UnitTypeId.REFINERY):
                    await self.build(UnitTypeId.REFINERY, near=vespene_geyser, placement_step=1)
            # Stavba Barracks
            # Bot staví tak dlouho, dokud si může dovolit stavět Barracks a jejich počet je menší než 6
            if self.tech_requirement_progress(UnitTypeId.BARRACKS) == 1:
                # Je jich méně než 6 nebo se již nějaké nestaví
                if self.structures(UnitTypeId.BARRACKS).amount < 6:
                    if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
                        await self.build(
                            UnitTypeId.BARRACKS,
                            near=command_center.position.towards(self.game_info.map_center, 8))

            if self.tech_requirement_progress(UnitTypeId.FACTORY) == 1:
                # Je jich méně než 6 nebo se již nějaké nestaví
                if self.structures(UnitTypeId.FACTORY).amount < 3:
                    if self.can_afford(UnitTypeId.FACTORY) and not self.already_pending(UnitTypeId.FACTORY):
                        await self.build(
                            UnitTypeId.FACTORY,
                            near=command_center.position.towards(self.game_info.map_center, 8))

            # Trénování jednotky Marine
            # Pouze, má-li bot postavené Barracks a může si jednotku dovolit
            if self.structures(UnitTypeId.BARRACKS) and self.can_afford(UnitTypeId.MARINE):
                # Každá budova Barracks trénuje v jeden čas pouze jednu jednotku (úspora zdrojů)
                for barrack in self.structures(UnitTypeId.BARRACKS).idle:
                    barrack.train(UnitTypeId.MARINE)

            # Add Stalker production for air defense
            if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.can_afford(UnitTypeId.STALKER):
                for gateway in self.structures(UnitTypeId.GATEWAY).ready.idle:
                    gateway.train(UnitTypeId.STALKER)

            # Add Siege Tank production for ground defense
            if self.structures(UnitTypeId.FACTORY).ready and self.can_afford(UnitTypeId.SIEGETANK):
                for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
                    factory.train(UnitTypeId.SIEGETANK)

            # Add Viking production for air defense
            if self.structures(UnitTypeId.STARPORT).ready and self.can_afford(UnitTypeId.VIKING):
                for starport in self.structures(UnitTypeId.STARPORT).ready.idle:
                    starport.train(UnitTypeId.VIKING)

            # Add Medivac production for support
            if self.structures(UnitTypeId.STARPORT).ready and self.can_afford(UnitTypeId.MEDIVAC):
                for starport in self.structures(UnitTypeId.STARPORT).ready.idle:
                    starport.train(UnitTypeId.MEDIVAC)

            # Útok s jednotkou Marine
            # Má-li bot více než 15 volných jednotek Marine, zaútočí na náhodnou nepřátelskou budovu nebo se přesune na jeho startovní pozici
            idle_marines = self.units(UnitTypeId.MARINE).idle
            if idle_marines.amount > 15:
                target = self.enemy_structures.random_or(
                    self.enemy_start_locations[0]).position
                for marine in idle_marines:
                    marine.attack(target)
            # Zbylý SCV bot pošle těžit minerály nejblíže Command Center
            for scv in self.workers.idle:
                if self.idle_worker_count > 7:
                    scv.gather(self.mineral_field.closest_to(command_center))
                else:
                    scv.gather(self.vespene_geyser.closest_to(command_center))

# Run the game
run_game(maps.get("sc2-ai-cup-2022"), [
    Bot(Race.Terran, workerRushBotK()),
    Computer(Race.Terran, Difficulty.Medium)
], realtime=False)
