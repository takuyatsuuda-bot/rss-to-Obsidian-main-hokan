import { useState, useEffect } from 'react';
import { type RewardItem, REWARD_DATA } from '../data/rewards';

export function useInventory() {
    const [inventoryIds, setInventoryIds] = useState<string[]>(() => {
        const saved = localStorage.getItem('kids-app-inventory');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('kids-app-inventory', JSON.stringify(inventoryIds));
    }, [inventoryIds]);

    const addItem = (item: RewardItem) => {
        setInventoryIds(prev => [...prev, item.id]);
    };

    const hasItem = (itemId: string) => inventoryIds.includes(itemId);

    // Get full item objects from IDs
    const inventoryItems = inventoryIds.map(id => REWARD_DATA.find(r => r.id === id)).filter(Boolean) as RewardItem[];

    return { inventoryItems, addItem, hasItem };
}
