import org.junit.Test;

import java.security.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.Assert.*;

public class TxHandlerTest {
    // Utilities
    private static byte[] copy(byte[] src) {
        return Arrays.copyOf(src, src.length);
    }
    private static Transaction deepCopy(Transaction src) {
        Transaction dest = new Transaction();
        dest.setHash(copy(src.getHash()));
        for (int i = 0; i < src.numInputs(); ++i) {
            dest.addInput(copy(src.getInput(i).prevTxHash), src.getInput(i).outputIndex);
            dest.addSignature(src.getInput(i).signature, i);
        }
        for (Transaction.Output output : src.getOutputs()) {
            dest.addOutput(output.value, output.address);
        }
        return dest;
    }
    private static byte[] sign(PrivateKey key, byte[] message)
            throws NoSuchAlgorithmException, InvalidKeyException, SignatureException {
        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initSign(key);
        signature.update(message);
        return signature.sign();
    }
    private static UTXOPool poolFromGenesis(Transaction genesis) {
        UTXOPool pool = new UTXOPool();
        for (int i = 0; i < genesis.numOutputs(); ++i) {
            pool.addUTXO(new UTXO(genesis.getHash(), i), genesis.getOutput(i));
        }
        return pool;
    }
    private class TxBuilder {
        private final Transaction mTransaction = new Transaction();
        private final List<PrivateKey> mKeys = new ArrayList<>();
        private TxBuilder input(byte[] srcHash, int srcIndex, PrivateKey key) {
            mTransaction.addInput(srcHash, srcIndex);
            mKeys.add(key);
            return this;
        }
        private TxBuilder output(double value, PublicKey address) {
            mTransaction.addOutput(value, address);
            return this;
        }
        private Transaction create() throws NoSuchAlgorithmException, InvalidKeyException, SignatureException {
            for (int i = 0; i < mKeys.size(); ++i) {
                mTransaction.addSignature(sign(mKeys.get(i), mTransaction.getRawDataToSign(i)), i);
            }
            mTransaction.finalize();
            return mTransaction;
        }
    }

    @Test
    public void handleTxs() throws NoSuchAlgorithmException, SignatureException, InvalidKeyException {
        KeyPairGenerator gen = KeyPairGenerator.getInstance("RSA");
        gen.initialize(512);
        KeyPair A = gen.generateKeyPair();
        KeyPair B = gen.generateKeyPair();

        Transaction genesis = new Transaction();
        genesis.addOutput(10, A.getPublic());
        genesis.addOutput(20, B.getPublic());
        genesis.finalize();

        Transaction tx = new TxBuilder()
                .input(genesis.getHash(), 0, A.getPrivate())
                .output(10, B.getPublic())
                .create();
        Transaction tx1 = new TxBuilder()
                .input(tx.getHash(), 0, B.getPrivate())
                .output(10, A.getPublic())
                .create();

        // Simple example: A wants to give B all her coin
        MaxFeeTxHandler handler = new MaxFeeTxHandler(poolFromGenesis(genesis));
        Transaction[] result = handler.handleTxs(new Transaction[] { tx });
        assertEquals(1, result.length);

        // Now B gives it back
        result = handler.handleTxs(new Transaction[] { tx1 });
        assertEquals(1, result.length);

        // Double spend
        result = handler.handleTxs(new Transaction[] { tx });
        assertEquals(0, result.length);

        // Double spend in one block
        handler = new MaxFeeTxHandler(poolFromGenesis(genesis));
        result = handler.handleTxs(new Transaction[] { tx, tx });
        assertEquals(1, result.length);

        // A -> B -> A in one block
        handler = new MaxFeeTxHandler(poolFromGenesis(genesis));
        result = handler.handleTxs(new Transaction[] { tx, tx1 });
        assertEquals(2, result.length);

        // A -> B -> A in an unfavorable order
        handler = new MaxFeeTxHandler(poolFromGenesis(genesis));
        result = handler.handleTxs(new Transaction[] { tx1, tx });
        assertEquals(2, result.length);
    }

    @Test
    public void isValidTx() throws NoSuchAlgorithmException, InvalidKeyException, SignatureException {
        KeyPairGenerator gen = KeyPairGenerator.getInstance("RSA");
        gen.initialize(512);
        KeyPair A = gen.generateKeyPair();
        KeyPair B = gen.generateKeyPair();

        Transaction genesis = new Transaction();
        genesis.addOutput(10, A.getPublic());
        genesis.addOutput(20, B.getPublic());
        genesis.finalize();

        // Simple example: A wants to give B all her coin
        TxHandler handler = new TxHandler(poolFromGenesis(genesis));
        Transaction tx = new Transaction();
        tx.addInput(genesis.getHash(), 0);
        tx.addOutput(10, B.getPublic());
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(0)), 0);
        tx.finalize();
        assertTrue(handler.isValidTx(tx));
        assertTrue(handler.isValidTx(deepCopy(tx)));
        Transaction tx0 = tx;

        // Some valid variations

        // A. Underspending
        tx = deepCopy(tx0);
        tx.getOutput(0).value = 9;
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(0)), 0);
        assertTrue(handler.isValidTx(tx));

        // B. Coin splitting
        tx = deepCopy(tx0);
        tx.getOutput(0).value = 6;
        tx.addOutput(4, A.getPublic());
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(0)), 0);
        assertTrue(handler.isValidTx(tx));

        // Generate a series of corruptions & check they're not valid

        // 1 UTXO does not exist (bad hash)
        tx = deepCopy(tx0);
        tx.getInput(0).prevTxHash = new byte[] { 1, 2, 3 };
        assertFalse(handler.isValidTx(tx));

        // 1.b UTXO does not exist (bad index)
        tx = deepCopy(tx0);
        tx.getInput(0).outputIndex = 10;
        assertFalse(handler.isValidTx(tx));

        // 2 Not signed
        tx = deepCopy(tx0);
        tx.addSignature(null, 0);
        assertFalse(handler.isValidTx(tx));

        // 2.b Signed by wrong person
        tx = deepCopy(tx0);
        tx.addSignature(sign(B.getPrivate(), tx.getRawDataToSign(0)), 0);
        assertFalse(handler.isValidTx(tx));

        // 3. UTXO claimed multiple times
        tx = deepCopy(tx0);
        tx.addInput(genesis.getHash(), 0);
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(0)), 0);
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(1)), 1);
        assertFalse(handler.isValidTx(tx));

        // 4. Negative output
        tx = deepCopy(tx0);
        tx.getOutput(0).value = -2;
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(0)), 0);
        assertFalse(handler.isValidTx(tx));

        // 5. Spending too much coin
        tx = deepCopy(tx0);
        tx.getOutput(0).value = 11;
        tx.addSignature(sign(A.getPrivate(), tx.getRawDataToSign(0)), 0);
        assertFalse(handler.isValidTx(tx));

        // Check we haven't corrupted the original
        assertTrue(handler.isValidTx(tx0));
    }
}