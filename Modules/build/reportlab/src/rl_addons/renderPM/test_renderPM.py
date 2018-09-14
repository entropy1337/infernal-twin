if  __name__=='__main__':
    import sys, os, traceback
    import _renderPM
    from reportlab.graphics import shapes, renderPM
    from reportlab.rl_config import verbose

    def test_base():
        class dummy:
            pass
        g=_renderPM.gstate(1,1)
        try:
            g.aaa = 3
            print('Wrong handling of bad attribute')
        except AttributeError:
            if verbose: print('bad attribute handled ok')

        for fontName, fontSize in (('aaa',10),('Times-Roman','10'),('Times-Roman',-10),(1,10)):
            try:
                g.setFont(fontName,fontSize)
                print('Wrong handling of setFont(%s,%s)' % (fontName,fontSize))
            except _renderPM.Error:
                if verbose: print('_renderPM.error detected OK')
            except TypeError:
                if verbose: print('Type detected OK')

        for a in ('strokeColor','fillColor'):
            try:
                setattr(g,a,(1,2,3))
                print('Wrong handling of bad '+a)
            except ValueError:
                if verbose: print('wrong handling of bad %s detected OK' % a)

            try:
                c=dummy()
                c.red=0xff/255.
                c.green=0xaf/255.
                c.blue=0xbf/255.
                for v,r in ((None,None),(0xfffafb,0xfffafb),(c,0xffafbf)):
                    setattr(g,a,v)
                    assert getattr(g,a)==r, "%s should be %s" % (a,hex(r))
                if verbose: print('setattr(%s) OK' % a)
            except:
                print('wrong handling of good %s' % a)
                traceback.print_exc()
                print(hex(getattr(g,a)))

        for v in ('a',1,(1,'a'),('a',1),(1,()),(1,('a',2))):
            try:
                g.dashArray=v
                print('Wrong handling of dashArray %s' % v)
            except ValueError:
                if verbose: print('Wrong handling of dashArray %s detected OK' % v)
        try:
            g.dashArray=7,(1,2,3)
            assert g.dashArray==(7.0,(1.0,2.0,3.0)), "should be (7.0,(1.0,2.0,3.0))"
            if verbose: print('dashArray obtained OK')
        except:
            print('wrong handling of dashArray')
            traceback.print_exc()
            print(g.dashArray)

        try:
            g.pathBegin()
            g.moveTo(0,0)
            g.lineTo(1,0)
            g.lineTo(1,1)
            g.lineTo(0,1)
            g.pathClose()
            good = (('moveToClosed', 0.0, 0.0), ('lineTo', 1.0, 0.0), ('lineTo', 1.0, 1.0), ('lineTo', 0.0, 1.0), ('lineTo', 0.0, 0.0))
            assert good==g.path, 'Wrong path should be %s' % str(good)
            if verbose: print('path attribute obtained OK')
        except:
            print('wrong handling of path')
            traceback.print_exc()
            print(g.path)

    if len(sys.argv)==1:
        test_base()
    else:
        def do_save(c,n,txt=0,pil=0):
            DIR='pmout'
            if not os.path.isdir(DIR): os.mkdir(DIR)
            c.saveToFile(os.path.join(DIR,"test_renderPM_%03d.gif"%n))
            if txt:
                f = open(os.path.join(DIR,"test_renderPM_%03d.txt"%n),'w')
                b = c.pixBuf
                w = c.width
                h = c.height
                k = 0
                for i in range(h):
                    f.write('%6.6x: '% i );
                    for j in range(w):
                        v = (ord(b[k])<<16) | (ord(b[k+1])<<8) | ord(b[k+2])
                        k = k + 3
                        f.write(' %6.6x'%v)
                    f.write('\n')

                if pil:
                    from PIL import Image
                    im = Image.new('RGB', size=(w, h))
                    im.fromstring(b)
                    f.write('PIL\n')
                    for i in range(h):
                        f.write('%6.6x: '% i );
                        for j in range(w):
                            v = im.getpixel((i,j))
                            f.write(' %2.2x%2.2x%2.2x'%v)
                        f.write('\n')
                    im.save(os.path.join(DIR,"test_renderPM_%03dx.jpg"%n),'JPEG')
                    im.save(os.path.join(DIR,"test_renderPM_%03dx.bmp"%n),'BMP')
                    im.save(os.path.join(DIR,"test_renderPM_%03dx.tif"%n),'TIFF')
                    im = im.convert("P", dither=Image.NONE, palette=Image.ADAPTIVE)
                    im.save(os.path.join(DIR,"test_renderPM_%03dx.gif"%n),'GIF')

        def flagged(n):
            return str(n) in sys.argv or 'all' in sys.argv

        def doVPath(c, S,x0=0,y0=0):
            c.pathBegin()
            for P in S:
                c.moveTo(P[0][0]-x0,P[0][1]-y0)
                for p in P[1:]:
                    c.lineTo(p[0]-x0,p[1]-y0)
                c.pathClose()
            c.pathFill()

        def doCTest(f, c, x, y, c0=0x8000,c1=0xff0000):
            c.ctm=(1,0,0,1,x,y)
            c.fillColor = c0
            c.strokeColor = c1
            f(c)

        if flagged(0):
            vp=[[(136.262,131.996), (136.91,130.502), (137.038,130.192), (137.18,129.832), (137.243,129.646), (137.295,129.464), (137.329,129.292), (137.342,129.134), (137.337,129.021), (137.321,128.92), (137.295,128.828), (137.26,128.747), (137.214,128.674), (137.159,128.61), (137.094,128.555), (137.02,128.506), (136.937,128.465), (136.845,128.43), (136.745,128.401), (136.636,128.377), (136.393,128.343), (136.118,128.324), (136.118,128), (140.816,128), (140.816,128.324), (140.578,128.345), (140.361,128.387), (140.164,128.449), (139.985,128.53), (139.824,128.627), (139.677,128.741), (139.544,128.869), (139.423,129.01), (139.313,129.164), (139.211,129.328), (139.116,129.502), (139.026,129.683), (138.858,130.066), (138.692,130.466), (134.642,140.186), (134.318,140.186), (130.034,130.142), (129.838,129.706), (129.743,129.514), (129.648,129.339), (129.553,129.18), (129.457,129.037), (129.358,128.908), (129.256,128.794), (129.148,128.694), (129.036,128.607), (128.916,128.532), (128.789,128.469), (128.652,128.417), (128.506,128.376), (128.349,128.345), (128.18,128.324), (128.18,128), (131.924,128), (131.924,128.324), (131.673,128.346), (131.426,128.377), (131.193,128.423), (131.084,128.453), (130.981,128.491), (130.887,128.535), (130.801,128.587), (130.725,128.648), (130.661,128.719), (130.609,128.8), (130.57,128.893), (130.546,128.998), (130.538,129.116), (130.549,129.253), (130.58,129.406), (130.625,129.567), (130.682,129.732), (130.811,130.053), (130.934,130.322), (131.654,131.996), (136.262,131.996)],
                [(136.028,132.644), (131.924,132.644), (133.994,137.45), (136.028,132.644)]]

            def doTest0(c, vp, x, y, c0=0x0,c1=0xff0000, angle=0, c2=0xff00ff):
                c.ctm=(1,0,0,1,x,y)
                c.fillColor = c0
                doVPath(c,vp,128,128)
                c.ctm = shapes.mmult(c.ctm, shapes.rotate(180))
                c.fillColor = c1
                doVPath(c,vp,128,128)
                c.ctm=(1,0,0,1,x,y)
                c.pathBegin()
                c.ctm=(1,0,0,1,x+20,y)
                c.ctm = shapes.mmult(c.ctm, shapes.rotate(angle))
                c.moveTo(0,0)
                c.lineTo(20,0)
                c.strokeColor = c2
                c.pathStroke()
                c.ctm=(1,0,0,1,x+20,y-20)
                c.drawString(0,0,"Robin")

            c = renderPM.PMCanvas(256, 256, bg=0xffffff)
            c.fillColor = 0x000000
            c.setFont('Times-Roman',18)

            doTest0(c,vp, 128, 128 )
            vp[0].reverse()
            vp[1].reverse()
            doTest0(c,vp, 168, 168, c0=0xff00, c1=0xff, angle=45)
            do_save(c,0)

        def doCPath1(c):
            c.pathBegin()
            c.moveTo(110-85,100-85)
            c.curveTo(110-85,94.477152501999996-85, 105.522847498-85,90-85, 100-85,90-85)
            c.curveTo(94.477152501999996-85,90-85, 90-85,94.477152501999996-85, 90-85,100-85)
            c.curveTo(90-85,105.522847498-85, 94.477152501999996-85,110-85, 100-85,110-85)
            c.curveTo(105.522847498-85,110-85, 110-85,105.522847498-85, 110-85,100-85)
            c.pathClose()
            c.pathFill()
            c.pathStroke()

        def doCPath2(c):
            c.pathBegin()
            c.moveTo(5,5)
            c.lineTo(5,20)
            c.lineTo(20,20)
            c.lineTo(20,5)
            c.pathClose()
            c.pathFill()

        def rotate_alpha_blend_text(can,off_x, text, dw, n, end_alpha):
            "decrease alpha linearly over the range of n points"
            dalpha = end_alpha/n
            for ii in range(n):
                can.gsave()
                can.rotate(dw*ii)
                # print dw*ii
                can.gstate.fill_opacity = end_alpha-ii*dalpha
                print("alpha = ", can.gstate.fill_opacity)
                can.drawString(off_x,0, text)
                can.grestore()

        def doCPath4(c,doStroke=1,doFill=1):
            c.pathBegin()
            c.moveTo(5,5)
            c.lineTo(5,20)
            c.lineTo(20,20)
            c.lineTo(20,5)
            c.pathClose()
            if doFill: c.pathFill()
            if doStroke: c.pathStroke()

        def doCPath5(c,doStroke=1):
            c.pathBegin()
            c.moveTo(5,5)
            c.lineTo(5,20)
            c.lineTo(20,20)
            c.lineTo(20,5)
            c.pathClose()
            if doStroke: c.pathStroke()

        def doCPath6(c,doStroke=1):
            c.pathBegin()
            c.moveTo(5,10)
            c.lineTo(5,20)
            c.lineTo(20,20)
            c.lineTo(20,10)
            c.pathClose()
            if doStroke: c.pathStroke()

        if flagged(1):
            c = renderPM.PMCanvas(25, 25, bg=0xffffff)
            c.setFont('Times-Roman',18)
            doCTest(doCPath1, c, 0, 0 )
            do_save(c,1)

        if flagged(2):
            c = renderPM.PMCanvas(25, 25, bg=0xffffff)
            doCTest(doCPath2, c, 0, 0 )
            do_save(c,2,txt=1,pil=1)

        if flagged(3):
            c = renderPM.PMCanvas(256, 256, bg=0xffffff)
            c.fillColor = 0x000000
            c.setFont('Times-Roman',18)
            text = "ABC"
            c.ctm=(1,0,0,("invert" in sys.argv) and -1 or 1, 127.5,127.5)
            c.drawString(0, 0, text)
            c.ctm = shapes.mmult(c.ctm, shapes.rotate(180))
            c.fillColor = 0xff0000
            c.drawString(0, 0, text)
            do_save(c,3)

        if flagged(4):
            c = renderPM.PMCanvas(25, 25, bg=0xffffff)
            doCTest(doCPath4, c, 0, 0, c0=0x8000, c1=0xff0000)
            do_save(c,4)

        if flagged(5):
            c = renderPM.PMCanvas(25, 25, bg=0xffffff)
            doCTest(doCPath5, c, 0, 0 )
            do_save(c,5)

        if flagged(6):
            c = renderPM.PMCanvas(250, 250, bg=0xffffff)
            c.pathBegin()
            c.moveTo(50,50)
            c.lineTo(50,200)
            c.lineTo(200,200)
            c.lineTo(200,50)
            c.pathClose()
            c.clipPathSet()
            c.pathBegin()
            c.moveTo(100,20)
            c.lineTo(100,220)
            c.lineTo(180,220)
            c.lineTo(180,20)
            c.pathClose()
            c.strokeColor = 0xff0000
            c.fillColor = 0x00ff00
            c.pathFill()
            #c.pathStroke()
            c.clipPathClear()
            do_save(c,6)

        if flagged(7):
            p=[('moveTo', 4.0, 0.0), ('lineTo', 4.0, 35.800000000000004), ('lineTo', 19.850000000000001, 35.800000000000004), ('curveTo', 22.350000000000001, 35.800000000000004, 24.650000000000002, 1.2325000000000002, 27.0, 34.850000000000001), ('curveTo', 30.650000000000002, 33.450000000000003, 32.600000000000001, 1.6300000000000001, 32.600000000000001, 26.0), ('curveTo', 32.600000000000001, 20.25, 28.650000000000002, 1.4325000000000001, 22.550000000000001, 16.350000000000001), ('lineTo', 22.550000000000001, 16.25), ('curveTo', 24.350000000000001, 15.4, 26.5, 1.3250000000000002, 29.300000000000001, 9.75), ('lineTo', 35.550000000000004, 0.0), ('lineTo', 29.600000000000001, 0.0), ('lineTo', 24.900000000000002, 7.4000000000000004), ('curveTo', 19.800000000000001, 15.450000000000001, 18.150000000000002, 0.9075000000000002, 14.200000000000001, 15.800000000000001), ('lineTo', 8.75, 15.800000000000001), ('lineTo', 8.75, 0.0), ('lineTo', 4.0, 0.0), ('closePath',), ('moveTo', 57.300000000000004, 8.3499999999999996), ('lineTo', 61.800000000000004, 7.8000000000000007), ('curveTo', 60.5, 2.9000000000000004, 56.850000000000001, 2.8425000000000002, 50.450000000000003, -0.60000000000000009), ('curveTo', 42.400000000000006, -0.60000000000000009, 38.050000000000004, 1.9025000000000003, 38.050000000000004, 12.75), ('curveTo', 38.050000000000004, 20.650000000000002, 42.300000000000004, 2.1150000000000002, 50.200000000000003, 26.5), ('curveTo', 52.400000000000006, 26.5, 62.350000000000001, 3.1175000000000002, 61.950000000000003, 11.850000000000001), ('lineTo', 42.550000000000004, 11.850000000000001), ('curveTo', 42.900000000000006, 5.6500000000000004, 46.550000000000004, 2.3275000000000001, 50.450000000000003, 3.0), ('curveTo', 55.400000000000006, 3.0, 56.75, 2.8375000000000004, 57.300000000000004, 8.3499999999999996), ('closePath',), ('moveTo', 67.300000000000011, -9.9500000000000011), ('lineTo', 67.300000000000011, 25.900000000000002), ('lineTo', 71.300000000000011, 25.900000000000002), ('lineTo', 71.300000000000011, 22.550000000000001), ('lineTo', 71.400000000000006, 22.550000000000001), ('curveTo', 72.150000000000006, 23.75, 74.100000000000009, 3.7050000000000005, 78.800000000000011, 26.5), ('curveTo', 86.150000000000006, 26.5, 89.800000000000011, 4.4900000000000011, 89.800000000000011, 13.15), ('curveTo', 89.800000000000011, 3.9500000000000002, 84.200000000000003, 4.21, 78.5, -0.60000000000000009), ('curveTo', 75.400000000000006, -0.60000000000000009, 73.100000000000009, 3.6550000000000007, 71.800000000000011, 2.7000000000000002), ('lineTo', 71.700000000000003, 2.7000000000000002), ('lineTo', 71.700000000000003, -9.9500000000000011), ('lineTo', 67.300000000000011, -9.9500000000000011), ('closePath',), ('moveTo', 93.450000000000003, 12.950000000000001), ('curveTo', 93.450000000000003, 15.75, 93.900000000000006, 4.6950000000000003, 96.100000000000009, 22.200000000000003), ('curveTo', 98.450000000000003, 25.200000000000003, 102.2, 5.1100000000000003, 105.60000000000001, 26.5), ('curveTo', 111.05000000000001, 26.5, 117.75, 5.8875000000000002, 117.75, 13.350000000000001), ('curveTo', 117.75, 7.8000000000000007, 116.35000000000001, 5.8175000000000008, 115.15000000000001, 3.8000000000000003), ('curveTo', 112.7, 0.80000000000000004, 109.05000000000001, 5.4525000000000006, 105.60000000000001, -0.60000000000000009), ('curveTo', 102.10000000000001, -0.60000000000000009, 98.450000000000003, 4.9225000000000003, 96.0, 3.8000000000000003), ('curveTo', 93.600000000000009, 6.8000000000000007, 93.450000000000003, 4.6725000000000003, 93.450000000000003, 12.950000000000001), ('closePath',), ('moveTo', 184.80000000000001, 17.949999999999999), ('lineTo', 180.50000000000003, 18.5), ('curveTo', 181.00000000000003, 20.800000000000001, 182.20000000000002, 9.1100000000000012, 192.20000000000002, 26.5), ('curveTo', 202.25000000000003, 26.5, 202.25000000000003, 10.112500000000002, 202.25000000000003, 16.75), ('lineTo', 202.25000000000003, 10.850000000000001), ('curveTo', 202.25000000000003, 4.2000000000000002, 202.25000000000003, 10.112500000000002, 203.65000000000003, 0.0), ('lineTo', 199.05000000000001, 0.0), ('curveTo', 198.35000000000002, 1.3500000000000001, 198.25000000000003, 9.9125000000000014, 198.15000000000003, 3.2000000000000002), ('curveTo', 194.45000000000002, 0.050000000000000003, 191.40000000000003, 9.5700000000000021, 188.60000000000002, -0.60000000000000009), ('curveTo', 182.90000000000003, -0.60000000000000009, 179.75000000000003, 8.9875000000000025, 179.75000000000003, 6.8500000000000005), ('curveTo', 179.75000000000003, 13.75, 187.10000000000002, 9.3550000000000022, 189.95000000000002, 14.950000000000001), ('curveTo', 190.60000000000002, 15.050000000000001, 195.35000000000002, 9.7675000000000018, 197.85000000000002, 16.449999999999999), ('curveTo', 197.95000000000002, 19.25, 198.00000000000003, 9.9000000000000021, 191.55000000000001, 22.900000000000002), ('curveTo', 186.05000000000001, 22.900000000000002, 185.35000000000002, 9.2675000000000018, 184.80000000000001, 17.949999999999999), ('closePath',), ('moveTo', 213.10000000000002, 0.0), ('lineTo', 209.00000000000003, 0.0), ('lineTo', 209.00000000000003, 35.800000000000004), ('lineTo', 213.40000000000003, 35.800000000000004), ('lineTo', 213.40000000000003, 23.0), ('lineTo', 213.50000000000003, 23.0), ('curveTo', 214.10000000000002, 23.900000000000002, 216.20000000000005, 10.810000000000002, 220.50000000000003, 26.5), ('curveTo', 227.50000000000003, 26.5, 231.50000000000003, 11.575000000000003, 231.50000000000003, 13.350000000000001), ('curveTo', 231.50000000000003, 2.4000000000000004, 224.45000000000005, 11.222500000000004, 220.30000000000004, -0.60000000000000009), ('curveTo', 219.20000000000005, -0.60000000000000009, 215.60000000000002, 10.780000000000001, 213.20000000000005, 3.25), ('lineTo', 213.10000000000002, 3.25), ('lineTo', 213.10000000000002, 0.0), ('closePath',)]
            c = renderPM.PMCanvas(400, 200, bg=0xffffff)
            c.strokeWidth = 0
            c.strokeColor = 0xff0000
            c.fillColor = 0x00ff00
            c.pathStroke()
            c.pathFill()
            do_save(c,7)
