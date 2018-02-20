import java.util.*;

public class MaxFeeTxHandler {
    private UTXOPool mPool;

    /**
     * Creates a public ledger whose current UTXOPool (collection of unspent transaction outputs) is
     * {@code utxoPool}. This should make a copy of utxoPool by using the UTXOPool(UTXOPool uPool)
     * constructor.
     */
    public MaxFeeTxHandler(UTXOPool utxoPool) {
        mPool = new UTXOPool(utxoPool);
    }

    /**
     * @return true if:
     * (1) all outputs claimed by {@code tx} are in the current UTXO pool,
     * (2) the signatures on each input of {@code tx} are valid,
     * (3) no UTXO is claimed multiple times by {@code tx},
     * (4) all of {@code tx}s output values are non-negative, and
     * (5) the sum of {@code tx}s input values is greater than or equal to the sum of its output
     *     values; and false otherwise.
     */
    public boolean isValid(Transaction tx) {
        return tryValid(mPool, tx);
    }

    private static boolean tryValid(UTXOPool pool, Transaction tx) {
        final Set<UTXO> claimed = new HashSet<>();
        double totalInput = 0;
        for (int i = 0; i < tx.numInputs(); ++i) {
            Transaction.Input input = tx.getInput(i);
            UTXO utxo = new UTXO(input.prevTxHash, input.outputIndex);
            if (!pool.contains(utxo) || claimed.contains(utxo)) {
                return false;
            }
            Transaction.Output src = pool.getTxOutput(utxo);
            if (input.signature == null ||
                    !Crypto.verifySignature(src.address, tx.getRawDataToSign(i), input.signature)) {
                return false;
            }
            claimed.add(utxo);
            totalInput += src.value;
        }
        double totalOutput = 0;
        for (Transaction.Output output : tx.getOutputs()) {
            if (output.value < 0) {
                return false;
            }
            totalOutput += output.value;
        }
        if (totalInput < totalOutput) {
            return false;
        }
        return true;
    }
    private static class Attempt {
        public final List<Transaction> log;
        public final double fee;
        public final UTXOPool pool;
        public Attempt(List<Transaction> log, double fee, UTXOPool pool) {
            this.log = log;
            this.fee = fee;
            this.pool = pool;
        }
        public boolean betterThan(Attempt other) {
            if (this.fee != other.fee) {
                return other.fee < this.fee;
            } else {
                return other.log.size() < this.log.size();
            }
        }
    }
    private static Attempt tryHandleTxs(UTXOPool pool, Transaction[] txs) {
        // Simple algorithm - process transactions in the order given, allowing them if valid
        pool = new UTXOPool(pool);
        ArrayList<Transaction> processed = new ArrayList<>();
        double totalFee = 0;
        for (Transaction tx : txs) {
            if (tryValid(pool, tx)) {
                for (Transaction.Input input : tx.getInputs()) {
                    UTXO utxo = new UTXO(input.prevTxHash, input.outputIndex);
                    totalFee += pool.getTxOutput(utxo).value;
                    pool.removeUTXO(utxo);
                }
                for (int i = 0; i < tx.numOutputs(); ++i) {
                    pool.addUTXO(new UTXO(tx.getHash(), i), tx.getOutput(i));
                    totalFee -= tx.getOutput(i).value;
                }
                processed.add(tx);
            }
        }
        return new Attempt(processed, totalFee, pool);
    }

    private static List<Transaction[]> permutations(Transaction[] xs) {
        if (xs.length == 0) {
            List<Transaction[]> result = new ArrayList<>();
            result.add(xs);
            return result;
        } else {
            List<Transaction[]> base = permutations(Arrays.copyOf(xs, xs.length - 1));
            for (int i = 0; i < base.size(); ++i) {
                Transaction[] b = Arrays.copyOf(base.get(i), xs.length);
                b[xs.length - 1] = xs[xs.length - 1];
                base.set(i, b);
            }
            List<Transaction[]> result = new ArrayList<>();
            for (int position = 0; position < xs.length; ++position) {
                for (Transaction[] b : base) {
                    Transaction[] r = Arrays.copyOf(b, b.length);
                    Transaction tmp = r[position];
                    r[position] = r[r.length - 1];
                    r[r.length - 1] = tmp;
                    result.add(r);
                }
            }
            return result;
        }
    }

    /**
     * Handles each epoch by receiving an unordered array of proposed transactions, checking each
     * transaction for correctness, returning a mutually valid array of accepted transactions, and
     * updating the current UTXO pool as appropriate.
     */
    public Transaction[] handleTxs(Transaction[] possibleTxs) {
        // BRUTE FORCE!!!
        //System.out.println(Arrays.toString(possibleTxs));
        Attempt bestAttempt = null;
        for (Transaction[] candidate : permutations(possibleTxs)) {
            Attempt attempt = tryHandleTxs(mPool, candidate);
            //System.out.println(String.format("%s -> %s (%f)", Arrays.toString(candidate), attempt.log, attempt.fee));
            if (bestAttempt == null || attempt.betterThan(bestAttempt)) {
                bestAttempt = attempt;
            }
        }
        mPool = bestAttempt.pool;
        return bestAttempt.log.toArray(new Transaction[0]);
    }
}
