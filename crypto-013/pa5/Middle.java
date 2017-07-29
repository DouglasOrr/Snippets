import java.math.BigInteger;
import java.util.HashMap;

class Middle {
    public static void main(String[] args) {
        BigInteger p = new BigInteger(args[0]);
        BigInteger g = new BigInteger(args[1]);
        BigInteger h = new BigInteger(args[2]);
        long xmax = Long.parseLong(args[3]);

        System.err.println(String.format("# p=%s\n# g=%s\n# h=%s\n# xmax=%s", p, g, h, xmax));

        long b = (long) Math.sqrt(xmax);
        BigInteger gb = g.modPow(BigInteger.valueOf(b), p);
        System.err.println(String.format("# b=%s\n# gb=%s", b, gb));

        HashMap<BigInteger, Long> lefts = new HashMap<BigInteger, Long>();
        for (long x1 = 0; x1 <= b; ++x1) {
            BigInteger lhs = g.modPow(BigInteger.valueOf(x1), p).modInverse(p).multiply(h).mod(p);
            lefts.put(lhs, x1);
        }
        for (long x0 = 0; x0 <= b; ++x0) {
            BigInteger rhs = gb.modPow(BigInteger.valueOf(x0), p);
            Long x1 = lefts.get(rhs);
            if (x1 != null) {
                long x = x0 * b + x1;
                System.out.println(x);
                System.err.println(String.format("# Check: %b", g.modPow(BigInteger.valueOf(x), p).equals(h)));
                return;
            }
        }
        System.err.println("# No solution found");
    }
}
