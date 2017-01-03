"""
Table definitions for Redshift written using SQL Alchemy's SQL Expression Language. In combination with the
sqlalchemy-redshift dialect (https://pypi.python.org/pypi/sqlalchemy-redshift) this provides us with an elegant way
to version control our schema and begin to build up a library of Python modules for querying against it.

To generate the DDL statements needed by the server-provisioning repository's bootstrap.sh script, run:

$ python models.py

"""
from hearthstone.enums import GameTag
from sqlalchemy import (
	Table, Column, BOOLEAN, SMALLINT, INT, BIGINT, PrimaryKeyConstraint, ForeignKeyConstraint,
	String, MetaData, ForeignKey, DATE, DATETIME, create_engine
)

metadata = MetaData()


game = Table('game', metadata,
	Column('id', BIGINT, primary_key=True, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('match_start', DATETIME, nullable=False, info={'encode': 'lzo'}),
	Column('game_type', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('region', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('num_turns', SMALLINT, nullable=False, info={'encode': 'delta'}),
	Column('game_length_seconds', INT, nullable=False, info={'encode': 'delta32k'}),
	Column('ladder_season', INT, nullable=False, info={'encode': 'runlength'}),
	Column('brawl_season', INT, info={'encode': 'lzo'}),
	Column('scenario_id', INT, info={'encode': 'lzo'})
)


player = Table('player', metadata,
	Column('game_id', None, ForeignKey('game.id'), nullable=False, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('player_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('entity_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('deck_id', BIGINT, nullable=False, info={'encode': 'lzo'}),
	Column('archetype_id', INT, info={'encode': 'lzo'}),
	Column('final_state', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('region', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('account_lo', INT, nullable=False, info={'encode': 'raw'}),
	Column('is_first', BOOLEAN, nullable=False, info={'encode': 'raw'}),
	Column('is_ai', BOOLEAN, nullable=False, info={'encode': 'runlength'}),
	Column('options_visible', BOOLEAN, nullable=False, info={'encode': 'raw'}),
	Column('full_deck_known', BOOLEAN, nullable=False, info={'encode': 'raw'}),
	Column('player_class', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('starting_hero_dbf_id', INT, nullable=False, info={'encode': 'bytedict'}),
	# Legend rank=0 (and then legend_rank field must be populated)
	Column('rank', SMALLINT, nullable=False, default=-1, info={'encode': 'lzo'}),
	Column('legend_rank', INT, info={'encode': 'lzo'}),
	# e.g. {"<dbf_id>": <num_copies>,...,"<dbf_id>":<num_copies>}
	Column('deck_list', String(65535), default='{}', info={'encode': 'lzo'}),
	PrimaryKeyConstraint('game_id', 'player_id', name='player_pk')
)

block = Table('block', metadata,
	Column('id', BIGINT, primary_key=True, info={'encode': 'lzo'}),
	Column('game_id', None, ForeignKey('game.id'), nullable=False, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('block_type', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('entity_id', SMALLINT, nullable=False, info={'encode': 'bytedict'}),
	Column('turn', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('step', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('entity_dbf_id', INT, info={'encode': 'lzo'}),
	Column('entity_player_id', SMALLINT, info={'encode': 'lzo'}),
	Column('parent_id', BIGINT, info={'encode': 'lzo'}),
	Column('target_entity_id', SMALLINT, info={'encode': 'lzo'}),
	Column('target_entity_dbf_id', INT, info={'encode': 'lzo'}),
	ForeignKeyConstraint(['game_id', 'entity_player_id'], ['player.game_id', 'player.player_id'])
)

block_info = Table('block_info', metadata,
	Column('block_id', None, ForeignKey('block.id'), nullable=False, info={'encode': 'lzo'}),
	Column('game_id', None, ForeignKey('game.id'), nullable=False, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('meta_data_type', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('info_entity_id', SMALLINT, nullable=False, info={'encode': 'bytedict'}),
	Column('data', INT, nullable=False, info={'encode': 'delta'}),
	Column('info_entity_dbf_id', INT, info={'encode': 'lzo'}),
)

choices = Table('choices', metadata,
	Column('block_id', None, ForeignKey('block.id'), nullable=False, info={'encode': 'lzo'}),
	Column('game_id', None, ForeignKey('game.id'), nullable=False, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('player_entity_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('choices_block_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('entity_id', SMALLINT, nullable=False, info={'encode': 'bytedict'}),
	Column('chosen', BOOLEAN, nullable=False, info={'encode': 'raw'}),
	Column('choice_type', SMALLINT, nullable=False, info={'encode': 'runlength'}),
	Column('entity_dbf_id', INT, info={'encode': 'lzo'}),
	Column('source_entity_id', SMALLINT, info={'encode': 'lzo'}),
)


# ***** An Example Options Block *****
# <Options id="62" ts="2016-12-13T02:30:38.847036-05:00">
#     <Option index="0" type="2" />
#     <Option EntityName="Raven Idol" entity="31" index="1" type="3">
#         <SubOption entity="32" index="0" />
#         <SubOption entity="33" index="1" />
#     </Option>
#     <Option EntityName="Living Roots" entity="101" index="2" type="3">
#         <SubOption entity="102" index="0">
#             <Target EntityName="Malfurion Stormrage" entity="82" index="0" />
#             <Target EntityName="Garrosh Hellscream" entity="84" index="1" />
#             <Target EntityName="Fel Orc Soulfiend" entity="53" index="2" />
#             <Target EntityName="Gadgetzan Auctioneer" entity="43" index="3" />
#         </SubOption>
#         <SubOption entity="103" index="1" />
#     </Option>
# </Options>
options = Table('options', metadata,
	Column('game_id', None, ForeignKey('game.id'), nullable=False, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('player_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('player_final_state', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('turn', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('step', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('options_block_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('option_index', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('option_type', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('option_entity_id', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('option_entity_dbf_id', INT, info={'encode': 'lzo'}),
	Column('suboption_index', SMALLINT, info={'encode': 'lzo'}),
	Column('suboption_entity_id', SMALLINT, info={'encode': 'lzo'}),
	Column('suboption_entity_dbf_id', INT, info={'encode': 'lzo'}),
	Column('target_index', SMALLINT, info={'encode': 'lzo'}),
	Column('target_entity_id', SMALLINT, info={'encode': 'lzo'}),
	Column('target_entity_dbf_id', INT, info={'encode': 'lzo'}),
	Column('sent', BOOLEAN, info={'encode': 'raw'}),
	Column('sent_position', SMALLINT, info={'encode': 'lzo'}),
	Column('sent_suboption', SMALLINT, info={'encode': 'lzo'}),
	Column('sent_target', SMALLINT, info={'encode': 'lzo'}),
	ForeignKeyConstraint(['game_id', 'player_id'], ['player.game_id', 'player.player_id'])
)

#TODO: Add TRANSFORMED_FROM_CARD (for Malchezar
entity_state = Table('entity_state', metadata,
	Column('game_id', None, ForeignKey('game.id'), nullable=False, info={'distkey': True, 'encode': 'lzo'}),
	Column('game_date', DATE, nullable=False, info={'sortkey': True, 'encode': 'lzo'}),
	Column('entity_id', SMALLINT, nullable=False, info={'encode': 'bytedict', 'tag': GameTag.ENTITY_ID}),
	Column('turn', SMALLINT, nullable=False, info={'encode': 'lzo', 'tag': GameTag.TURN}),
	Column('step', SMALLINT, nullable=False, info={'encode': 'lzo', 'tag': GameTag.STEP}),
	Column('entity_in_initial_entities', BOOLEAN, nullable=False, info={'encode': 'raw'}),
	Column('entered_zone_on', SMALLINT, info={'encode': 'lzo'}),
	Column('dbf_id', INT, info={'encode': 'lzo'}),
	Column('before_block_id', None, ForeignKey('block.id'), info={'encode': 'lzo'}),
	Column('after_block_id', None, ForeignKey('block.id'), info={'encode': 'lzo'}),
	Column('controller', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CONTROLLER}),
	Column('controller_final_state', SMALLINT, nullable=False, info={'encode': 'lzo'}),
	Column('last_affected_by_dbf_id', INT, info={'encode': 'lzo'}),
	Column('attached_dbf_id', INT, info={'encode': 'lzo'}),
	Column('zone', SMALLINT, nullable=False, info={'encode': 'lzo', 'tag': GameTag.ZONE}),
	Column('cost', INT, info={'encode': 'lzo', 'tag': GameTag.COST}),
	Column('atk', INT, info={'encode': 'lzo', 'tag': GameTag.ATK}),
	Column('health', INT, info={'encode': 'lzo', 'tag': GameTag.HEALTH}),
	Column('armor', INT, info={'encode': 'lzo', 'tag': GameTag.ARMOR}),
	Column('durability', INT, info={'encode': 'lzo', 'tag': GameTag.DURABILITY}),
	Column('damage', INT, info={'encode': 'lzo', 'tag': GameTag.DAMAGE}),
	Column('taunt', BOOLEAN, info={'encode': 'raw', 'tag': GameTag.TAUNT}),
	Column('stealth', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.STEALTH}),
	Column('divine_shield', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.DIVINE_SHIELD}),
	Column('deathrattle', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.DEATHRATTLE}),
	Column('zone_position', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.ZONE_POSITION}),
	Column('spellpower', INT, info={'encode': 'lzo', 'tag': GameTag.SPELLPOWER}),
	Column('charge', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CHARGE}),
	Column('silenced', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SILENCED}),
	Column('windfury', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.WINDFURY}),
	Column('last_affected_by', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.LAST_AFFECTED_BY}),
	Column('frozen', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.FROZEN}),
	Column('enraged', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.ENRAGED}),
	Column('overload', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.OVERLOAD}),
	Column('secret', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SECRET}),
	Column('combo', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.COMBO}),
	Column('fatigue', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.FATIGUE}),
	Column('current_player', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CURRENT_PLAYER}),
	Column('first_player', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.FIRST_PLAYER}),
	Column('resources_used', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.RESOURCES_USED}),
	Column('resources', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.RESOURCES}),
	Column('hero_entity', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HERO_ENTITY}),
	Column('attached', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.ATTACHED}),
	Column('exhausted', BOOLEAN, info={'encode': 'raw', 'tag': GameTag.EXHAUSTED}),
	Column('owner', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.OWNER}),
	Column('elite', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.ELITE}),
	Column('next_step', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NEXT_STEP}),
	Column('class', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CLASS}),
	Column('card_set', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CARD_SET}),
	Column('cardrace', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CARDRACE}),
	Column('faction', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.FACTION}),
	Column('cardtype', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CARDTYPE}),
	Column('rarity', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.RARITY}),
	Column('state', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.STATE}),
	Column('cant_attack', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CANT_ATTACK}),
	Column('cant_play', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CANT_PLAY}),
	Column('immune', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.IMMUNE}),
	Column('just_played', BOOLEAN, info={'encode': 'raw', 'tag': GameTag.JUST_PLAYED}),
	Column('linked_entity', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.LINKED_ENTITY}),
	Column('combo_active', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.COMBO_ACTIVE}),
	Column('card_target', INT, info={'encode': 'lzo', 'tag': GameTag.CARD_TARGET}),
	Column('num_cards_played_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_CARDS_PLAYED_THIS_TURN}),
	Column('cant_be_targeted_by_opponents', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CANT_BE_TARGETED_BY_OPPONENTS}),
	Column('num_turns_in_play', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_TURNS_IN_PLAY}),
	Column('num_turns_left', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_TURNS_LEFT}),
	Column('current_spellpower', INT, info={'encode': 'lzo', 'tag': GameTag.CURRENT_SPELLPOWER}),
	Column('temp_resources', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.TEMP_RESOURCES}),
	Column('overload_owed', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.OVERLOAD_OWED}),
	Column('num_attacks_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_ATTACKS_THIS_TURN}),
	Column('first_card_played_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.FIRST_CARD_PLAYED_THIS_TURN}),
	Column('mulligan_state', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.MULLIGAN_STATE}),
	Column('cant_be_targeted_by_spells', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CANT_BE_TARGETED_BY_SPELLS}),
	Column('shouldexitcombat', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SHOULDEXITCOMBAT}),
	Column('creator', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CREATOR}),
	Column('parent_card', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.PARENT_CARD}),
	Column('num_minions_played_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_MINIONS_PLAYED_THIS_TURN}),
	Column('collectible', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.COLLECTIBLE}),
	Column('cant_be_targeted_by_hero_powers', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CANT_BE_TARGETED_BY_HERO_POWERS}),
	Column('health_minimum', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HEALTH_MINIMUM}),
	Column('tag_one_turn_effect', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.TAG_ONE_TURN_EFFECT}),
	Column('hand_revealed', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.HAND_REVEALED}),
	Column('adjacent_buff', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.ADJACENT_BUFF}),
	Column('spellpower_double', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.SPELLPOWER_DOUBLE}),
	Column('healing_double', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HEALING_DOUBLE}),
	Column('num_options_played_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_OPTIONS_PLAYED_THIS_TURN}),
	Column('to_be_destroyed', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.TO_BE_DESTROYED}),
	Column('aura', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.AURA}),
	Column('poisonous', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.POISONOUS}),
	Column('hero_power_double', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HERO_POWER_DOUBLE}),
	Column('ai_must_play', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.AI_MUST_PLAY}),
	Column('num_minions_player_killed_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_MINIONS_PLAYER_KILLED_THIS_TURN}),
	Column('num_minions_killed_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_MINIONS_KILLED_THIS_TURN}),
	Column('affected_by_spell_power', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.AFFECTED_BY_SPELL_POWER}),
	Column('extra_deathrattles', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.EXTRA_DEATHRATTLES}),
	Column('start_with_1_health', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.START_WITH_1_HEALTH}),
	Column('immune_while_attacking', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.IMMUNE_WHILE_ATTACKING}),
	Column('multiply_hero_damage', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.MULTIPLY_HERO_DAMAGE}),
	Column('topdeck', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.TOPDECK}),
	Column('hero_power', INT, info={'encode': 'lzo', 'tag': GameTag.HERO_POWER}),
	Column('deathrattle_return_zone', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.DEATHRATTLE_RETURN_ZONE}),
	Column('steady_shot_can_target', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.STEADY_SHOT_CAN_TARGET}),
	Column('displayed_creator', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.DISPLAYED_CREATOR}),
	Column('powered_up', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.POWERED_UP}),
	Column('spare_part', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SPARE_PART}),
	Column('forgetful', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.FORGETFUL}),
	Column('overload_locked', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.OVERLOAD_LOCKED}),
	Column('num_times_hero_power_used_this_game', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_TIMES_HERO_POWER_USED_THIS_GAME}),
	Column('current_heropower_damage_bonus', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.CURRENT_HEROPOWER_DAMAGE_BONUS}),
	Column('heropower_damage', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HEROPOWER_DAMAGE}),
	Column('last_card_played', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.LAST_CARD_PLAYED}),
	Column('num_friendly_minions_that_died_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_TURN}),
	Column('num_cards_drawn_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_CARDS_DRAWN_THIS_TURN}),
	Column('inspire', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.INSPIRE}),
	Column('receives_double_spelldamage_bonus', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.RECEIVES_DOUBLE_SPELLDAMAGE_BONUS}),
	Column('heropower_additional_activations', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HEROPOWER_ADDITIONAL_ACTIVATIONS}),
	Column('heropower_activations_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.HEROPOWER_ACTIVATIONS_THIS_TURN}),
	Column('revealed', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.REVEALED}),
	Column('num_friendly_minions_that_died_this_game', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_GAME}),
	Column('cannot_attack_heroes', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CANNOT_ATTACK_HEROES}),
	Column('lock_and_load', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.LOCK_AND_LOAD}),
	Column('discover', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.DISCOVER}),
	Column('shadowform', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SHADOWFORM}),
	Column('num_friendly_minions_that_attacked_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_FRIENDLY_MINIONS_THAT_ATTACKED_THIS_TURN}),
	Column('num_resources_spent_this_game', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.NUM_RESOURCES_SPENT_THIS_GAME}),
	Column('choose_both', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CHOOSE_BOTH}),
	Column('heavily_armored', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.HEAVILY_ARMORED}),
	Column('dont_show_immune', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.DONT_SHOW_IMMUNE}),
	Column('ritual', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.RITUAL}),
	Column('overload_this_game', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.OVERLOAD_THIS_GAME}),
	Column('spells_cost_health', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SPELLS_COST_HEALTH}),
	Column('transformed_from_card', INT, info={'encode': 'lzo', 'tag': GameTag.TRANSFORMED_FROM_CARD}),
	Column('cthun', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CTHUN}),
	Column('shifting', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SHIFTING}),
	Column('jade_golem', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.JADE_GOLEM}),
	Column('embrace_the_shadow', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.EMBRACE_THE_SHADOW}),
	Column('choose_one', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CHOOSE_ONE}),
	Column('extra_attacks_this_turn', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.EXTRA_ATTACKS_THIS_TURN}),
	Column('seen_cthun', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.SEEN_CTHUN}),
	Column('untouchable', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.UNTOUCHABLE}),
	Column('red_mana_crystals', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.RED_MANA_CRYSTALS}),
	Column('autoattack', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.AUTOATTACK}),
	Column('arms_dealing', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.ARMS_DEALING}),
	Column('tag_last_known_cost_in_hand', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.TAG_LAST_KNOWN_COST_IN_HAND}),
	Column('kazakus_potion_power_1', INT, info={'encode': 'lzo', 'tag': GameTag.KAZAKUS_POTION_POWER_1}),
	Column('kazakus_potion_power_2', INT, info={'encode': 'lzo', 'tag': GameTag.KAZAKUS_POTION_POWER_2}),
	Column('modify_definition_attack', INT, info={'encode': 'lzo', 'tag': GameTag.MODIFY_DEFINITION_ATTACK}),
	Column('modify_definition_health', INT, info={'encode': 'lzo', 'tag': GameTag.MODIFY_DEFINITION_HEALTH}),
	Column('modify_definition_cost', INT, info={'encode': 'lzo', 'tag': GameTag.MODIFY_DEFINITION_COST}),
	Column('multiple_classes', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.MULTIPLE_CLASSES}),
	Column('all_targets_random', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.ALL_TARGETS_RANDOM}),
	Column('multi_class_group', SMALLINT, info={'encode': 'lzo', 'tag': GameTag.MULTI_CLASS_GROUP}),
	Column('card_costs_health', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.CARD_COSTS_HEALTH}),
	Column('grimy_goons', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.GRIMY_GOONS}),
	Column('jade_lotus', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.JADE_LOTUS}),
	Column('kabal', BOOLEAN, info={'encode': 'runlength', 'tag': GameTag.KABAL}),
	Column('additional_play_reqs_1', INT, info={'encode': 'lzo', 'tag': GameTag.ADDITIONAL_PLAY_REQS_1}),
	Column('additional_play_reqs_2', INT, info={'encode': 'lzo', 'tag': GameTag.ADDITIONAL_PLAY_REQS_2}),
	Column('tag_script_data_num_1', INT, info={'encode': 'lzo', 'tag': GameTag.TAG_SCRIPT_DATA_NUM_1}),
	Column('tag_script_data_num_2', INT, info={'encode': 'lzo', 'tag': GameTag.TAG_SCRIPT_DATA_NUM_2}),
	Column('tag_script_data_ent_1', INT, info={'encode': 'lzo', 'tag': GameTag.TAG_SCRIPT_DATA_ENT_1}),
	Column('tag_script_data_ent_2', INT, info={'encode': 'lzo', 'tag': GameTag.TAG_SCRIPT_DATA_ENT_2}),
	# 65535 Is the MAX Bytes for a VARCHAR in Redshift
	Column('tags', String(65535), info={'encode': 'lzo'})
)

if __name__ == '__main__':
	"""Print The Create Table DDL Statements"""
	from sqlalchemy.schema import CreateTable
	from sqlalchemy_redshift.dialect import RedshiftDialect
	for table_obj in metadata.sorted_tables:
		table_sql = CreateTable(table_obj).compile(dialect=RedshiftDialect())
		print(table_sql)

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--apply', dest='connection', action='store')
	args = parser.parse_args()
	if args.connection:
		engine = create_engine(args.connection)
		metadata.create_all(engine)
