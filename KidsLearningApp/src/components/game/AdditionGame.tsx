import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useInventory } from '../../hooks/useInventory';
import { REWARD_DATA } from '../../data/rewards';
import { Check } from 'lucide-react';

interface AdditionGameProps { }

export function AdditionGame({ }: AdditionGameProps) {
    const [num1, setNum1] = useState(1);
    const [num2, setNum2] = useState(1);
    const [options, setOptions] = useState<number[]>([]);
    const [score, setScore] = useState(0);
    const [showReward, setShowReward] = useState(false);
    const [rewardItem, setRewardItem] = useState(REWARD_DATA[0]);
    const { addItem } = useInventory();
    const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);

    useEffect(() => {
        generateQuestion();
    }, []);

    const generateQuestion = () => {
        const n1 = Math.floor(Math.random() * 5) + 1; // 1-5
        const n2 = Math.floor(Math.random() * 4) + 1; // 1-4
        setNum1(n1);
        setNum2(n2);

        const ans = n1 + n2;
        // Generate simple options
        const opts = new Set<number>();
        opts.add(ans);
        while (opts.size < 3) {
            const r = Math.floor(Math.random() * 9) + 2; // Random 2-10
            if (r !== ans) opts.add(r);
        }
        setOptions(Array.from(opts).sort(() => Math.random() - 0.5));
        setFeedback(null);
    };

    const handleAnswer = (selected: number) => {
        if (selected === num1 + num2) {
            setFeedback('correct');
            const newScore = score + 1;
            setScore(newScore);

            if (newScore > 0 && newScore % 3 === 0) {
                const randomReward = REWARD_DATA[Math.floor(Math.random() * REWARD_DATA.length)];
                setRewardItem(randomReward);
                addItem(randomReward);
                setTimeout(() => setShowReward(true), 500);
            } else {
                setTimeout(generateQuestion, 1000);
            }
        } else {
            setFeedback('wrong');
            setTimeout(() => setFeedback(null), 500);
        }
    };

    const handleCloseReward = () => {
        setShowReward(false);
        generateQuestion();
    };

    return (
        <div className="flex flex-col items-center w-full max-w-2xl">
            <div className="w-full flex justify-between items-center mb-8">
                <div className="text-2xl font-bold text-green-600">⭐️ {score}</div>
            </div>

            <AnimatePresence>
                {showReward && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 flex items-center justify-center bg-black/50 z-50"
                    >
                        <div className="bg-white p-8 rounded-3xl flex flex-col items-center text-center shadow-2xl border-4 border-yellow-400">
                            <h2 className="text-3xl font-bold text-yellow-600 mb-4">やったー！</h2>
                            <div className="text-9xl mb-4 animate-bounce">{rewardItem.emoji}</div>
                            <p className="text-xl text-gray-600 mb-6">{rewardItem.name} をゲットしたよ！</p>
                            <button
                                onClick={handleCloseReward}
                                className="bg-green-500 text-white font-bold py-3 px-8 rounded-full text-xl hover:bg-green-600 transition-colors"
                            >
                                つぎへ
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="bg-white rounded-3xl p-8 shadow-xl w-full text-center border-4 border-green-100 relative overflow-hidden">
                {feedback === 'correct' && (
                    <motion.div
                        initial={{ scale: 0 }} animate={{ scale: 1.5 }}
                        className="absolute inset-0 flex items-center justify-center text-green-500/30 z-0 pointer-events-none"
                    >
                        <Check size={200} strokeWidth={4} />
                    </motion.div>
                )}
                {feedback === 'wrong' && (
                    <motion.div
                        initial={{ scale: 0 }} animate={{ scale: 1.5 }}
                        className="absolute inset-0 flex items-center justify-center text-red-500/30 z-0 pointer-events-none"
                    >
                        <div className="text-[200px] font-bold leading-none">❌</div>
                    </motion.div>
                )}

                <div className="flex justify-center items-center gap-4 mb-8 text-6xl font-bold text-gray-700 relative z-10">
                    <div className="flex flex-col items-center">
                        <div className="text-4xl mb-2 flex flex-wrap justify-center w-24">
                            {Array(num1).fill('🍎').map((_, i) => <span key={i} className="text-2xl">🍎</span>)}
                        </div>
                        <div>{num1}</div>
                    </div>

                    <div className="text-green-400">➕</div>

                    <div className="flex flex-col items-center">
                        <div className="text-4xl mb-2 flex flex-wrap justify-center w-24">
                            {Array(num2).fill('🍎').map((_, i) => <span key={`2-${i}`} className="text-2xl">🍎</span>)}
                        </div>
                        <div>{num2}</div>
                    </div>

                    <div className="text-green-400">🟰</div>

                    <div className="w-24 h-24 border-b-4 border-gray-300 flex items-center justify-center text-gray-400">
                        ?
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-6 relative z-10">
                    {options.map((option) => (
                        <motion.button
                            key={option}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleAnswer(option)}
                            animate={feedback === 'wrong' ? { x: [-10, 10, -10, 10, 0] } : {}}
                            className="aspect-video bg-green-100 hover:bg-green-200 text-green-700 text-6xl font-bold rounded-2xl flex items-center justify-center shadow-md border-b-4 border-green-300 active:border-b-0 active:translate-y-1 transition-all"
                        >
                            {option}
                        </motion.button>
                    ))}
                </div>
            </div>
        </div>
    );
}
