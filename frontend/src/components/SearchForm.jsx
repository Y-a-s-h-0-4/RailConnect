import { useState } from 'react';
import { Search, Calendar, MapPin, Shuffle } from 'lucide-react';
import { motion } from 'framer-motion';

export function SearchForm({ onSearch, isSearching }) {
    const [source, setSource] = useState('');
    const [destination, setDestination] = useState('');
    const [date, setDate] = useState('');
    const [criteria, setCriteria] = useState('fastest');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!source || !destination || !date) return;
        onSearch({ source, destination, date, criteria });
    };

    const swapStations = () => {
        setSource(destination);
        setDestination(source);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-4xl glass-card p-6 md:p-8"
        >
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">

                {/* Stations Input */}
                <div className="flex flex-col md:flex-row items-center gap-4 relative">
                    <div className="w-full md:w-1/2 relative group">
                        <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5 transition-colors group-focus-within:text-primary" />
                        <input
                            type="text"
                            placeholder="Leaving from..."
                            value={source}
                            onChange={(e) => setSource(e.target.value)}
                            className="w-full h-14 bg-background/50 border border-border rounded-xl pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                            required
                        />
                    </div>

                    <button
                        type="button"
                        onClick={swapStations}
                        className="md:absolute left-1/2 md:-translate-x-1/2 top-1/2 md:-translate-y-1/2 z-10 w-10 h-10 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center hover:bg-primary hover:text-primary-foreground hover:scale-110 transition-all shadow-md group"
                    >
                        <Shuffle className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                    </button>

                    <div className="w-full md:w-1/2 relative group">
                        <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5 transition-colors group-focus-within:text-accent" />
                        <input
                            type="text"
                            placeholder="Going to..."
                            value={destination}
                            onChange={(e) => setDestination(e.target.value)}
                            className="w-full h-14 bg-background/50 border border-border rounded-xl pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
                            required
                        />
                    </div>
                </div>

                {/* Date & Criteria Input */}
                <div className="flex flex-col md:flex-row gap-4 lg:w-3/4 mx-auto">
                    <div className="w-full md:w-1/2 relative group">
                        <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5 transition-colors group-focus-within:text-primary" />
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full h-14 bg-background/50 border border-border rounded-xl pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-foreground"
                            required
                        />
                    </div>

                    <div className="w-full md:w-1/2 relative group">
                        <select
                            value={criteria}
                            onChange={(e) => setCriteria(e.target.value)}
                            className="w-full h-14 bg-background/50 border border-border rounded-xl px-4 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-foreground appearance-none cursor-pointer"
                        >
                            <option value="fastest">Fastest Route</option>
                            <option value="cheapest">Cheapest Route</option>
                            <option value="fewest_switches">Fewest Switches</option>
                        </select>
                    </div>
                </div>

                {/* Submit */}
                <div className="flex justify-center mt-2">
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="h-14 px-8 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded-xl flex items-center gap-2 transition-all hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:-translate-y-0"
                    >
                        <Search className="w-5 h-5" />
                        {isSearching ? 'Searching Trains...' : 'Find Routes'}
                    </button>
                </div>

            </form>
        </motion.div>
    );
}
