type QueryFormProps = {
    question: string;
    onSubmit: (newValue: string) => void;
    onChange: (value: string) => void;
    clearField: () => void;
};

export const QueryForm = ({
    question,
    onSubmit,
    onChange,
    clearField,
}: QueryFormProps) => {
    return (
        <div className="flex gap-4 w-full">
            <div className="flex gap-4 w-full bg-slate-800 border focus-within:border-white border-slate-600 rounded px-4 py-2">
                <input
                    className="bg-slate-800 text-white w-full outline-none focus:outline-none"
                    value={question}
                    onChange={(e) => {
                        onChange(e.target.value);
                    }}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            onSubmit(question);
                        }
                    }}
                    placeholder="Ask a question..."
                ></input>
                <button
                    className={`text-white/60 cursor-pointer hover:bg-gray-800 transition-opacity duration-130 ${
                        question.trim() == ''
                            ? 'opacity-0 pointer-events-none'
                            : 'opacity-100 '
                    }`}
                    onClick={() => clearField()}
                >
                    Clear
                </button>
            </div>
            <button
                className="text-slate-900 bg-white cursor-pointer rounded px-2"
                onClick={() => onSubmit(question)}
            >
                Submit
            </button>
        </div>
    );
};
