from reportlab.rl_config import T1SearchPath
T1SearchPath.insert(0,'C:\\Python\\PyArt\\pdffonts')
import _renderPM
from time import time
from reportlab.pdfbase.pdfmetrics import getFont
from reportlab.pdfbase._fontdata import standardFonts
g = _renderPM.gstate(200,200)
g.ctm = (1,0,0,1,0,0)

N=20
t0 = time()
for i in range(N):
	for k in standardFonts:
		f = getFont(k)
		print(k, f.face.findT1File())
		_renderPM.makeT1Font(k,f.face.findT1File(),f.encoding.vector)

	_renderPM.delCache()
print('Reading %d standard fonts %d times took %.2f seconds' % (len(standardFonts),N,time()-t0))
