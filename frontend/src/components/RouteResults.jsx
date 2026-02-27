import { motion } from 'framer-motion';
import { ArrowRight, Clock, MapPin, IndianRupee } from 'lucide-react';

export function RouteResults({ routes, isLoading }) {
    if (isLoading) {
        return (
            <div className="w-full flex justify-center py-20">
                <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!routes || routes.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full text-center py-12 text-muted-foreground"
            >
                <p className="text-lg">No routes found. Please try a different search.</p>
            </motion.div>
        );
    }

    return (
        <div className="w-full max-w-4xl flex flex-col gap-6 mt-8">
            <h2 className="text-2xl font-bold mb-2">Available Routes</h2>
            {routes.map((route, index) => (
                <RouteCard key={index} route={route} index={index} />
            ))}
        </div>
    );
}

function RouteCard({ route, index }) {
    // route is a list of segments
    const totalDuration = calculateTotalDuration(route);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 flex flex-col gap-6 hover:border-primary/50 transition-colors"
        >
            <div className="flex justify-between items-center border-b border-border/50 pb-4">
                <div className="flex items-center gap-3">
                    <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                        {route.length === 1 ? 'Direct' : `${route.length - 1} Connection(s)`}
                    </span>
                </div>
                <div className="flex gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>{totalDuration} mins</span>
                    </div>
                </div>
            </div>

            <div className="flex flex-col gap-4 relative">
                {route.map((segment, idx) => (
                    <div key={idx} className="flex relative">
                        {/* Timeline line */}
                        {idx !== route.length - 1 && (
                            <div className="absolute left-3 top-8 bottom-[-16px] w-[2px] bg-border/50"></div>
                        )}

                        <div className="flex gap-4 w-full">
                            <div className="flex flex-col items-center z-10">
                                <div className="w-6 h-6 rounded-full bg-accent/20 border-2 border-accent flex items-center justify-center mt-1">
                                    <div className="w-2 h-2 rounded-full bg-accent" />
                                </div>
                            </div>

                            <div className="flex-1 bg-background/30 rounded-lg p-4 border border-border/30">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex flex-col">
                                        <span className="font-semibold text-lg">{segment.source}</span>
                                        <span className="text-xs text-muted-foreground">Departs {segment.departure_time}</span>
                                    </div>

                                    <div className="flex flex-col items-center px-4 text-muted-foreground">
                                        <ArrowRight className="w-5 h-5 mb-1" />
                                        <span className="text-[10px] font-mono tracking-wider">{segment.train_number}</span>
                                    </div>

                                    <div className="flex flex-col items-end">
                                        <span className="font-semibold text-lg">{segment.destination}</span>
                                        <span className="text-xs text-muted-foreground">Arrives {segment.arrival_time}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </motion.div>
    );
}

// Helper to mock calculate total duration from segments (since backend doesn't send it yet)
function calculateTotalDuration(route) {
    let total = 0;
    // VERY rough approximation for UI purposes
    route.forEach(s => total += s.duration || 120);
    return total;
}
