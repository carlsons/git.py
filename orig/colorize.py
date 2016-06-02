
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

ColorNames = [ 'BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE' ]

_Bold    = "\033[1m"
_Color1  = "\033[%dm"
_Color2  = "\033[%d;%dm"
_Bold2   = "\033[1;%d;%dm"
_Reset   = "\033[0m"

def seq_fg( color ):
   return _Color1 % ( color + 30 )

def seq_bg( color ):
   return _Color1 % ( color + 40 )

def seq_bold():
   return _Bold

def seq_reset():
   return _Reset

def seq_color( fg, bg, bold=False ):
   if bold:
      return _Bold2 % ( fg+30, bg+40 )
   return _Color2 % ( fg+30, bg+40 )

def colorize( text, fg=WHITE, bg=BLACK, bold=False ):
   output = [ seq_color( fg, bg, bold ), text, seq_reset() ]
   # print fg, bg, bold, output
   return ''.join( output )

def show():
   print "%8s : %12s %12s %12s %12s" % ( "Attrib", "normal", "bold", "background", "bold" )
   for c in range(8):
      fg_samp  = colorize( "texttexttext", fg=c                   )
      fgb_samp = colorize( "texttexttext", fg=c,         bold=1   )
      bg_samp  = colorize( "texttexttext",         bg=c           )
      bgb_samp = colorize( "texttexttext",         bg=c, bold=1   )
      print "%8s : %s %s %s %s" % ( ColorNames[c], fg_samp, fgb_samp, bg_samp, bgb_samp )

if __name__ == '__main__':
   show()


