import java.util.HashSet;
import java.util.Set;

public class CraftyMaliciousNode implements Node {
    private final Set<Transaction> mTransactions = new HashSet<>();
    private int mRoundsRemaining;

    public CraftyMaliciousNode(double p_graph, double p_malicious, double p_txDistribution, int numRounds) {
        mRoundsRemaining = numRounds;
    }

    public void setFollowees(boolean[] followees) {
    }

    public void setPendingTransaction(Set<Transaction> pendingTransactions) {
        mTransactions.addAll(pendingTransactions);
    }

    public Set<Transaction> sendToFollowers() {
        if (--mRoundsRemaining < 2) {
            return new HashSet<>(mTransactions);
        }
        return new HashSet<Transaction>();
    }

    public void receiveFromFollowees(Set<Candidate> candidates) {
    }
}
