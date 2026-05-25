export function Button({ className = "", ...props }: any) {
  return <button className={`inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 disabled:opacity-50 ${className}`} {...props} />
}
