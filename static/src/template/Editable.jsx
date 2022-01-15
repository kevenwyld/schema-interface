import React, { useState } from "react";

// From https://github.com/learnwithparam/logrocket-inline-edit-ui/
const Editable = ({
    text,
    type,
    placeholder,
    children,
    ...props
  }) => {
      
    const [isEditing, setEditing] = useState(false);

    // Event handler while pressing any key while editing
    const handleKeyDown = (e) => {
        const keys = ["Escape", "Tab", "Enter"];
        if (keys.indexOf({e}) > -1){
            setEditing(false);
        }
    };

    return (
        <section {...props}>
            {isEditing ? (
            <div
                onBlur={() => setEditing(false)}
                onKeyDown={e => handleKeyDown(e)}
            >
                {children}
            </div>
            ) : (
            <div
                onClick={() => setEditing(true)}
            >
                <span className={`${text ? "text-black" : "text-gray-500"}`}>
                {text || placeholder || ""}
                </span>
            </div>
            )}
        </section>
    );
};
    
export default Editable;