from otree.api import *
import random


class Constants(BaseConstants):
    name_in_url = "public_goods_punishment"
    players_per_group = 7
    num_rounds = 7
    endowment = 20
    efficiency_factor = 0.375
    punishment_costs = [0, 1, 2, 4, 6, 9, 12, 16, 20, 25, 30]


class Subsession(BaseSubsession):
    def creating_session(self):
        # This will randomize to group to a new set of players every round
        self.group_randomly(fixed_id_in_group=True)

        import random
        import itertools

        if self.round_number == 1:
            number_of_groups = len(self.get_groups())

            punishment_condition = itertools.cycle([True, False])
            for i, group in enumerate(self.get_groups(), start=1):
                choice = next(punishment_condition)
                print(f"Group {i} has{'' if choice else ' no'} punishment condition")
                group.punishment_condition = choice


class Group(BaseGroup):
    total_group_investment = models.CurrencyField()
    punishment_condition = models.BooleanField()

    def set_first_stage_earnings(self):
        players = self.get_players()
        self.total_group_investment = sum([p.public_investment for p in players])

        for p in players:
            p.payoff_from_private = p.endowment - p.public_investment 

            p.payoff_from_public = Constants.efficiency_factor * self.total_group_investment
            p.gross_profit = p.payoff_from_private + p.payoff_from_public


class Player(BasePlayer):
    # Existing investment field
    payoff_from_private = models.CurrencyField()
    payoff_from_public = models.CurrencyField()
    endowment = models.CurrencyField(initial=Constants.endowment)
    gross_profit = models.CurrencyField(initial=0)

    public_investment = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        verbose_name="How much would you like to invest in public account?",
    )

    received_punishment = models.CurrencyField(initial=0)
    total_punishment_cost = models.CurrencyField(initial=0)

    def set_punishment_and_final_payoffs(self):
        # Iterate over each group member once, assigning punishment and calculating costs
        for other_player in self.get_others_in_group():
            # Assign punishment points from this player to the other player
            punishment_points = getattr(self, f"punishment_sent_to_player_{other_player.id_in_group}")
            other_player.received_punishment += punishment_points

            # Add up the cost incurred for the punishment given
            self.total_punishment_cost += Constants.punishment_costs[punishment_points]

        punishment_reduction_proportion = min(1, self.received_punishment / 10)

        final_earnings = self.gross_profit * (1 - punishment_reduction_proportion)

        final_earnings -= self.total_punishment_cost

        self.payoff = max(0, final_earnings)


for i in range(1, Constants.players_per_group + 1):
    setattr(
        Player,
        f"punishment_sent_to_player_{i}",
        models.IntegerField(min=0, max=10, initial=None, label=f"Choose punishment for player #{i}"),
    )

    # def adjusted_round(self):
    #     return (
    #         self.subsession.round_number
    #         if self.subsession.round_number <= Constants.num_rounds // 2
    #         else self.subsession.round_number - Constants.num_rounds // 2
    #     )

    # def adjusted_game(self):
    #     return 1 if self.subsession.round_number <= Constants.num_rounds // 2 else 2
