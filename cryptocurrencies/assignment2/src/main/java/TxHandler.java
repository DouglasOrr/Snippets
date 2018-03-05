import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

public class TxHandler {
    private final UTXOPool mPool;

    /**
     * Creates a public ledger whose current UTXOPool (collection of unspent transaction outputs) is
     * {@code utxoPool}. This should make a copy of utxoPool by using the UTXOPool(UTXOPool uPool)
     * constructor.
     */
    public TxHandler(UTXOPool utxoPool) {
        mPool = new UTXOPool(utxoPool);
    }

    public UTXOPool getUTXOPool() {
        return mPool;
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
    public boolean isValidTx(Transaction tx) {
        final Set<UTXO> claimed = new HashSet<>();
        double totalInput = 0;
        for (int i = 0; i < tx.numInputs(); ++i) {
            Transaction.Input input = tx.getInput(i);
            UTXO utxo = new UTXO(input.prevTxHash, input.outputIndex);
            if (!mPool.contains(utxo) || claimed.contains(utxo)) {
                return false;
            }
            Transaction.Output src = mPool.getTxOutput(utxo);
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

    /**
     * Handles each epoch by receiving an unordered array of proposed transactions, checking each
     * transaction for correctness, returning a mutually valid array of accepted transactions, and
     * updating the current UTXO pool as appropriate.
     */
    public Transaction[] handleTxs(Transaction[] possibleTxs) {
        // Simple algorithm - process transactions in the order given, allowing them if valid
        ArrayList<Transaction> processed = new ArrayList<>();
        for (Transaction tx : possibleTxs) {
            if (isValidTx(tx)) {
                for (Transaction.Input input : tx.getInputs()) {
                    mPool.removeUTXO(new UTXO(input.prevTxHash, input.outputIndex));
                }
                for (int i = 0; i < tx.numOutputs(); ++i) {
                    mPool.addUTXO(new UTXO(tx.getHash(), i), tx.getOutput(i));
                }
                processed.add(tx);
            }
        }
        return processed.toArray(new Transaction[0]);
    }
}
