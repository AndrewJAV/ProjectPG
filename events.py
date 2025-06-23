from blinker import Signal

# Definición de señales
player_shoot = Signal('player_shoot')
player_aim = Signal('player_aim')
player_stop_aim = Signal('player_stop_aim')
weapon_equip = Signal('weapon_equip')
spawn_player_bullet = Signal('spawn_player_bullet')
spawn_enemy_bullet = Signal('spawn_enemy_bullet')