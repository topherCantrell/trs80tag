from trs80tag.coco_raaka_tu import CoCoRaakaTu

import sys
from coco_bedlam import CoCoBedlam

# trs80tag coco_raaka_tu colums=32 banner=true

games = [
    CoCoRaakaTu,
    CoCoBedlam,
]

def main(): 
       
    if len(sys.argv)<2:
        print('USAGE:')
        print('trs80tag game_name [columns=n] [banner=true]')
        print()
        print('GAME NAMES:')
        
        for game in games:
            print('*****',game.GAME_NAME,'*****')
            game.print_banner() 
            print()
            
        return   
    
    game_name = sys.argv[1]
    
    found_game = None
    for game in games:
        if game.GAME_NAME == game_name:
            found_game = game
            break
        
    if not found_game:
        print('## Unknown game name "'+game_name+'"')
        return
    
    ncols = found_game.NUM_COLUMNS
    banner = True
    for arg in sys.argv[2:]:
        if arg.startswith('columns='):
            try:
                ncols = int(arg[8:].strip())
            except Exception:
                ncols = -1
            if ncols<8:
                print('## Invalid:',arg)
                return
        elif arg.startswith('banner='):
            s = arg[7:].strip().upper()
            if s=='TRUE':
                banner = True
            elif s=='FALSE':
                banner = False
            else:
                print('## Invalid:',arg)
                return
        else:
            print('## Unknown argument:',arg)
            return
            
    if banner:
        found_game.print_banner()
        print()
        
    game = found_game(ncols)
    game.run_forever()
    game.print_flush()

main()
