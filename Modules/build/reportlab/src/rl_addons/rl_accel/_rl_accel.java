import org.python.core.*;
import java.text.*;
import java.io.*;

public class _rl_accel{
    public static String version = "0.30";
    private static String[] formats = {"#", "#.#", "#.##", "#.###", "#.####", "#.#####", "#.######"};

    public static Object fp_str(PyObject[] args){
        StringBuffer buffer = new StringBuffer();

        if(args.length==1 && args[0] instanceof PySequence){
            //iterate through the first element
            PySequence seq = (PySequence)args[0];
            for(int i=0;i<seq.__len__();i++){
                format(buffer, seq.__getitem__(i).toString());
            }
        }
        else{
            //iterate through the args list
            for(int i=0;i<args.length;i++){
                format(buffer, args[i].toString());
            }
        }
        return buffer.toString().trim();
    }

    private static double log_e_10 = Math.log(10.0);

    private static void format(StringBuffer buffer, String a){
        String num;
        int l;
        double d = Double.parseDouble(a);
        if(Math.abs(d)<=1.0e-7) num = "0";
        else{
            if(Math.abs(d)>1.0)
                l = (Math.min(Math.max(0,(6-(int)(Math.log(Math.abs(d))/log_e_10))),6));
            else l = 6;
            NumberFormat formatter = new DecimalFormat(formats[l]);
            num = formatter.format(d);
            if(num.startsWith("0")&&(num.length()>1))
                num = num.substring(1);
        }
        buffer.append(num).append(' ');
    }

	public static String escapePDF(String text){
		int textlen = text.length();
		StringBuffer out = new StringBuffer(textlen*4);
		int i=0;

		while(i<textlen){
			char c = text.charAt(i++);
			if((int)c<32 || (int)c>=127){
				String buf = Integer.toOctalString((int)c);
				out.append('\\');
				if(buf.length()<3){
					if(buf.length()<2)
						out.append('0');
					out.append('0');
				}
				out.append(buf);
				}
			else{
				if(c=='\\' || c=='(' || c==')')
					out.append('\\');
				out.append(c);
			}
		}

		return out.toString();
	}

	public static String _instanceEscapePDF(String text){
		return escapePDF(text);
	}

	static long a85_0 = 1;
	static long a85_1 = 85;
	static long a85_2 = 7225;
	static long a85_3 = 614125;
	static long a85_4 = 52200625;

	public static String _AsciiBase85Encode(String inData){
		int	length = inData.length();
		int blocks, extra, i, k, lim;
		long block, res;

		blocks = length / 4;
		extra = length % 4;

		StringBuffer buf = new StringBuffer((blocks+1)*5+3);
		lim = 4*blocks;

		for(k=i=0; i<lim; i += 4){
			/*
			 * If you evere have trouble with this consider using masking to ensure
			 * that the shifted quantity is only 8 bits long
			 */
			block = ((((int)inData.charAt(i))<<24)|(((int)inData.charAt(i+1))<<16)
					|(((int)inData.charAt(i+2))<<8)|(int)inData.charAt(i+3)) & 0x00000000FFFFFFFFL;
			if (block == 0) buf.append('z');
			else {
				res = block/a85_4;
				buf.append((char)(res+33));
				block -= res*a85_4;

				res = block/a85_3;
				buf.append((char)(res+33));
				block -= res*a85_3;

				res = block/a85_2;
				buf.append((char)(res+33));
				block -= res*a85_2;

				res = block / a85_1;
				buf.append((char)(res+33));

				buf.append((char)(block-res*a85_1+33));
				}
			}

		if(extra>0){
			block = 0L;

			for (i=0; i<extra; i++)
				block += ((long)inData.charAt(length-extra+i)) << (24-8*i);

			res = block/a85_4;
			buf.append((char)(res+33));
			if(extra>=1){
				block -= res*a85_4;

				res = block/a85_3;
				buf.append((char)(res+33));
				if(extra>=2){
					block -= res*a85_3;

					res = block/a85_2;
					buf.append((char)(res+33));
					if(extra>=3) buf.append((char)((block-res*a85_2)/a85_1+33));
					}
				}
			}

		buf.append('~');
		buf.append('>');
		return buf.toString();
	}
    public static final boolean isWhitespace(int ch){
        return (ch == 0 || ch == 9 || ch == 10 || ch == 12 || ch == 13 || ch == 32);
    	}
	public static String _AsciiBase85Decode(String inData){
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        int state = 0;
        int chn[] = new int[5];
	int len = inData.length();
        for(int k = 0; k<len; ++k){
            int ch = ((int)inData.charAt(k)) & 0xff;
            if(ch == '~') break;
            if(isWhitespace(ch)) continue;
            if (ch=='z' && state==0){
                out.write(0);
                out.write(0);
                out.write(0);
                out.write(0);
                continue;
            	}
            if (ch < '!' || ch > 'u') throw new RuntimeException("Illegal character in _AsciiBase85Decode.");
            chn[state] = ch - '!';
            ++state;
            if(state == 5){
                state = 0;
                int r = 0;
                for (int j = 0; j < 5; ++j) r = r*85 + chn[j];
                out.write((byte)(r>>24));
                out.write((byte)(r>>16));
                out.write((byte)(r>>8));
                out.write((byte)r);
            	}
        	}
        long r;
        if(state==1) throw new RuntimeException("Illegal length in _AsciiBase85Decode.");
        if (state == 2) {
            r = ((chn[0]*85+ chn[1])*85*85*85 + 0xfffff)&0x0ffffffffL;
            out.write((byte)(r>>24));
        }
        else if (state == 3) {
            r = (((chn[0]*85 + chn[1])*85 + chn[2])*85*85+0xffff)&0x0ffffffffL;
            out.write((byte)(r >> 24));
            out.write((byte)(r >> 16));
        }
        else if (state == 4) {
            r = ((((chn[0]*85 + chn[1])*85 + chn[2])*85 + chn[3])*85+0xff)&0x0ffffffffL;
            out.write((byte)(r >> 24));
            out.write((byte)(r >> 16));
            out.write((byte)(r >> 8));
        }
        return out.toString();
		}
		
		
	public static int calcChecksum(String data){
		int	 dl = data.length();
		int i;
		long sum = 0L;
		long n;
		int leftover;
		
		/*full ULONGs*/
		for(i=0;(dl-i)>=4;i+=4){
			n = ((int)data.charAt(i)) << 24;
			n += ((int)data.charAt(i+1)) << 16;
			n += ((int)data.charAt(i+2)) << 8;
			n += (int)data.charAt(i+3);
			sum += n;
			}
	
		/*pad with zeros*/
		leftover = dl & 3;
		if(leftover>0){
			n = ((int)data.charAt(i)) << 24;;
			if (leftover>1) n += ((int)data.charAt(i+1)) << 16;
			if (leftover>2) n += ((int)data.charAt(i+2)) << 8;
			sum += n;
			}
	
		return (int)sum;
	}
		
}
