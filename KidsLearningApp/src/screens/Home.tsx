import { motion } from 'framer-motion';

interface HomeProps {
    onStartHiragana: () => void;
    onStartAddition: () => void;
    onOpenRoom: () => void;
}

export function Home({ onStartHiragana, onStartAddition, onOpenRoom }: HomeProps) {
    return (
        <div className="min-h-screen bg-sky-100 flex flex-col items-center justify-center p-4">
            <motion.h1
                initial={{ y: -50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="text-5xl font-bold text-sky-600 mb-12 drop-shadow-md"
            >
                あそぼう！
            </motion.h1>

            <div className="grid gap-6 w-full max-w-md">
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onStartHiragana}
                    className="bg-pink-400 hover:bg-pink-500 text-white text-3xl font-bold py-6 px-8 rounded-3xl shadow-xl flex items-center justify-center gap-4 border-b-8 border-pink-600 active:border-b-0 active:translate-y-2 transition-all"
                >
                    <span>🅰️</span> ひらがな
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onStartAddition}
                    className="bg-green-400 hover:bg-green-500 text-white text-3xl font-bold py-6 px-8 rounded-3xl shadow-xl flex items-center justify-center gap-4 border-b-8 border-green-600 active:border-b-0 active:translate-y-2 transition-all"
                >
                    <span>➕</span> たしざん
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onOpenRoom}
                    className="bg-yellow-400 hover:bg-yellow-500 text-white text-3xl font-bold py-6 px-8 rounded-3xl shadow-xl flex items-center justify-center gap-4 border-b-8 border-yellow-600 active:border-b-0 active:translate-y-2 transition-all mt-8"
                >
                    <span>🏠</span> おへや
                </motion.button>
            </div>
        </div>
    );
}
