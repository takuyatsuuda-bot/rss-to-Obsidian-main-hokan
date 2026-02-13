import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HIRAGANA_DATA, type HiraganaChar } from '../../data/hiragana';
import { useInventory } from '../../hooks/useInventory';
import { REWARD_DATA } from '../../data/rewards';
import { Check } from 'lucide-react';

interface HiraganaGameProps { }

export function HiraganaGame({ }: HiraganaGameProps) {
    const [currentQuestion, setCurrentQuestion] = useState<HiraganaChar | null>(null);
    const [options, setOptions] = useState<string[]>([]);
    const [score, setScore] = useState(0);
    const [showReward, setShowReward] = useState(false);
    const [rewardItem, setRewardItem] = useState(REWARD_DATA[0]);
    const { addItem } = useInventory();
    const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);

    useEffect(() => {
        generateQuestion();
    }, []);

    const generateQuestion = () => {
        const randomIndex = Math.floor(Math.random() * HIRAGANA_DATA.length);
        const question = HIRAGANA_DATA[randomIndex];
        setCurrentQuestion(question);

        // Shuffle options
        const shuffled = [...question.options].sort(() => Math.random() - 0.5);
        setOptions(shuffled);
        setFeedback(null);
    };

    const handleAnswer = (selected: string) => {
        if (!currentQuestion) return;

        if (selected === currentQuestion.char) {
            setFeedback('correct');
            const newScore = score + 1;
            setScore(newScore);

            if (newScore > 0 && newScore % 3 === 0) { // Reward every 3 correct answers
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

    if (!currentQuestion) return <div>Loading...</div>;

    return (
        <div className="flex flex-col items-center w-full max-w-2xl">
            <div className="w-full flex justify-between items-center mb-8">
                <div className="text-2xl font-bold text-pink-500">⭐️ {score}</div>
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

            <div className="bg-white rounded-3xl p-8 shadow-xl w-full text-center border-4 border-pink-100 relative overflow-hidden">
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

                <div className="relative z-10">
                    <div className="text-9xl mb-4">{currentQuestion.emoji}</div>

                    <div className="grid grid-cols-3 gap-4">
                        {options.map((option) => (
                            <motion.button
                                key={option}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => handleAnswer(option)}
                                animate={feedback === 'wrong' ? { x: [-10, 10, -10, 10, 0] } : {}}
                                className="aspect-square bg-pink-100 hover:bg-pink-200 text-pink-600 text-6xl font-bold rounded-2xl flex items-center justify-center shadow-md border-b-4 border-pink-300 active:border-b-0 active:translate-y-1 transition-all"
                            >
                                {option}
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
