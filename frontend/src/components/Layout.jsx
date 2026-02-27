import { Train } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

export function Layout({ children }) {
    return (
        <div className="min-h-screen flex flex-col items-center">
            <header className="w-full h-20 glass flex items-center justify-between px-8 lg:px-24 sticky top-0 z-50">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center gap-3"
                >
                    <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
                        <Train className="w-6 h-6 text-primary" />
                    </div>
                    <h1 className="text-xl font-bold tracking-tight">Connecting Trains</h1>
                </motion.div>
            </header>

            <main className="flex-1 w-full max-w-6xl p-6 lg:p-10 flex flex-col gap-8 items-center">
                {children}
            </main>

            <footer className="w-full py-6 text-center text-sm text-muted-foreground mt-auto">
                <p>Built with ❤️ for train travelers.</p>
            </footer>
        </div>
    );
}
