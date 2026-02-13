import { useInventory } from '../hooks/useInventory';
import { motion } from 'framer-motion';

interface RoomProps {
    onBack: () => void;
}

export function Room({ onBack }: RoomProps) {
    const { inventoryItems } = useInventory();

    return (
        <div className="min-h-screen bg-amber-50 p-4 flex flex-col items-center">
            <div className="w-full max-w-4xl flex justify-between items-center mb-8">
                <button
                    onClick={onBack}
                    className="bg-orange-400 hover:bg-orange-500 text-white font-bold py-2 px-4 rounded-full shadow-lg transform active:scale-95 transition-all text-xl"
                >
                    ⬅️ もどる
                </button>
                <h1 className="text-3xl font-bold text-orange-600">おへや (My Room)</h1>
                <div className="w-12"></div> {/* Spacer */}
            </div>

            <div className="relative w-full max-w-4xl p-8 bg-white rounded-3xl shadow-xl border-4 border-orange-200 min-h-[60vh] flex flex-wrap content-start gap-4">
                {inventoryItems.length === 0 ? (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-xl">
                        まだ 何も ないよ！
                        <br />
                        クイズを クリアして
                        <br />
                        プレゼントを もらおう！
                    </div>
                ) : (
                    inventoryItems.map((item, index) => (
                        <motion.div
                            key={`${item.id}-${index}`}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            whileHover={{ scale: 1.2, rotate: 10 }}
                            drag
                            dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }} // Simplified drag: just jiggle in place or small movement
                            className="text-6xl cursor-pointer select-none"
                        >
                            {item.emoji}
                        </motion.div>
                    ))
                )}
            </div>
        </div>
    );
}
