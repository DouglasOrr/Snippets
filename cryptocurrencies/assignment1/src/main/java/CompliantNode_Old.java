import java.util.HashSet;
import java.util.Set;

public class CompliantNode_Old implements Node {
    private final Set<Transaction> mUnbroadcasted = new HashSet<>();
    private final Set<Transaction> mBroadcasted = new HashSet<>();
    private int mRoundsRemaining;

    public CompliantNode_Old(double p_graph, double p_malicious, double p_txDistribution, int numRounds) {
        mRoundsRemaining = numRounds;
    }

    public void setFollowees(boolean[] followees) {
    }

    public void setPendingTransaction(Set<Transaction> pendingTransactions) {
        mUnbroadcasted.addAll(pendingTransactions);
    }

    public Set<Transaction> sendToFollowers() {
        if (--mRoundsRemaining < 0) {
            HashSet<Transaction> consensus = new HashSet<>(mBroadcasted);
            consensus.addAll(mUnbroadcasted);
            return consensus;
        }
        HashSet<Transaction> result = new HashSet<>(mUnbroadcasted);
        mBroadcasted.addAll(mUnbroadcasted);
        mUnbroadcasted.clear();
        return result;
    }

    public void receiveFromFollowees(Set<Candidate> candidates) {
        for (Candidate candidate : candidates) {
            if (!mBroadcasted.contains(candidate.tx)) {
                mUnbroadcasted.add(candidate.tx);
            }
        }
    }
}
