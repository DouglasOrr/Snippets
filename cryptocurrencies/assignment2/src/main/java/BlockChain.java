// Block Chain should maintain only limited block nodes to satisfy the functions
// You should not have all the blocks added to the block chain in memory
// as it would cause a memory overflow.

import java.util.*;

public class BlockChain {
    public static final int CUT_OFF_AGE = 10;

    private static class Node implements Comparable<Node> {
        final Block block;
        final TxHandler handler;
        final int height;
        final int created;
        public Node(Block b, TxHandler t, int h, int c) {
            block = b;
            handler = t;
            height = h;
            created = c;
        }
        @Override
        public int compareTo(Node node) {
            if (this.height != node.height) {
                // Order for height: max=highest
                return Integer.compare(this.height, node.height);
            } else {
                // Opposite order for created time: max=oldest
                return Integer.compare(node.created, this.created);
            }
        }
    }
    private final TransactionPool mTransactionPool = new TransactionPool();
    private int clock = 0;
    private final Map<ByteArrayWrapper, Node> mNodes = new HashMap<>();

    private static TxHandler advancePool(UTXOPool source, Block block) {
        TxHandler handler = new TxHandler(source);
        // 1. Process the block
        if (handler.handleTxs(block.getTransactions().toArray(new Transaction[0])).length
                != block.getTransactions().size()) {
            return null;
        }
        // 2. Add the coinbase
        Transaction coinbase = block.getCoinbase();
        for (int output = 0; output < coinbase.numOutputs(); ++output) {
            handler.getUTXOPool().addUTXO(
                    new UTXO(coinbase.getHash(), output),
                    coinbase.getOutput(output));
        }
        return handler;
    }

    /**
     * create an empty block chain with just a genesis block. Assume {@code genesisBlock} is a valid
     * block
     */
    public BlockChain(Block genesisBlock) {
        mNodes.put(new ByteArrayWrapper(genesisBlock.getHash()),
                new Node(genesisBlock, advancePool(new UTXOPool(), genesisBlock), 0, clock++));
    }

    /** Get the transaction pool to mine a new block */
    public TransactionPool getTransactionPool() {
        return mTransactionPool;
    }

    /** Add a transaction to the transaction pool */
    public void addTransaction(Transaction tx) {
        mTransactionPool.addTransaction(tx);
    }

    /** Get the maximum height block */
    public Block getMaxHeightBlock() {
        return Collections.max(mNodes.values()).block;
    }

    /** Get the UTXOPool for mining a new block on top of max height block */
    public UTXOPool getMaxHeightUTXOPool() {
        // Defensive copy
        return new UTXOPool(Collections.max(mNodes.values()).handler.getUTXOPool());
    }

    /**
     * Add {@code block} to the block chain if it is valid. For validity, all transactions should be
     * valid and block should be at {@code height > (maxHeight - CUT_OFF_AGE)}.
     *
     * <p>
     * For example, you can try creating a new block over the genesis block (block height 2) if the
     * block chain height is {@code <=
     * CUT_OFF_AGE + 1}. As soon as {@code height > CUT_OFF_AGE + 1}, you cannot create a new block
     * at height 2.
     *
     * @return true if block is successfully added
     */
    public boolean addBlock(Block block) {
        // 0. Trying to mine a new genesis block
        if (block.getPrevBlockHash() == null) {
            return false;
        }
        Node parent = mNodes.get(new ByteArrayWrapper(block.getPrevBlockHash()));

        // 1. Either invalid, or reaching back by more than the maximum allowed height
        if (parent == null) {
            return false;
        }

        // 2. Contains invalid transactions
        TxHandler handler = advancePool(parent.handler.getUTXOPool(), block);
        if (handler == null) {
            return false;
        }

        // 3. Insert new block
        mNodes.put(new ByteArrayWrapper(block.getHash()), new Node(block, handler, parent.height + 1, clock++));

        // 4. Remove any blocks that are too deep to work from
        int maxHeight = Collections.max(mNodes.values()).height;
        mNodes.values().removeIf(node -> node.height < maxHeight - CUT_OFF_AGE);
        return true;
    }
}