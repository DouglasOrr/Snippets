import java.util.*;

public class CompliantNode implements Node {
    private final Set<Transaction> mUnbroadcasted = new HashSet<>();
    private final Map<Transaction, Set<Integer>> mVotes = new HashMap<>();
    private final double mPMalicious;
    private int mThreshold;
    private int mRoundsRemaining;

    public CompliantNode(double p_graph, double p_malicious, double p_txDistribution, int numRounds) {
        mPMalicious = p_malicious;
        mRoundsRemaining = numRounds;
    }

    public void setFollowees(boolean[] followees) {
        double t = 0;
        for (boolean f : followees) {
            if (f) {
                t += 1 - mPMalicious;
            }
        }
        mThreshold = (int) t;
    }

    public void setPendingTransaction(Set<Transaction> pendingTransactions) {
        mUnbroadcasted.addAll(pendingTransactions);
    }

    public Set<Transaction> sendToFollowers() {
        if (--mRoundsRemaining < 0) {
            HashSet<Transaction> consensus = new HashSet<>();
            for (Map.Entry<Transaction, Set<Integer>> entry : mVotes.entrySet()) {
                if (mThreshold <= entry.getValue().size()) {
                    consensus.add(entry.getKey());
                }
            }
            return consensus;
        }
        HashSet<Transaction> result = new HashSet<>(mUnbroadcasted);
        mUnbroadcasted.clear();
        return result;
    }

    public void receiveFromFollowees(Set<Candidate> candidates) {
        for (Candidate candidate : candidates) {
            if (!mVotes.containsKey(candidate.tx)) {
                mUnbroadcasted.add(candidate.tx);
                mVotes.put(candidate.tx, new HashSet<>(Collections.singleton(candidate.sender)));
            } else {
                mVotes.get(candidate.tx).add(candidate.sender);
            }
        }
    }
}
