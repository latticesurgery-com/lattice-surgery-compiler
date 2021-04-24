## MAKO TEMPLATE FOR GENERATING CIRCUIT RENDER IN LATEX
##
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{backgrounds,fit,decorations.pathreplacing,calc}

\begin{document}

\begin{tikzpicture}
    \tikzstyle{paulicomponent} = [draw,draw=none,fill=white,minimum size=1.5em] 
    \tikzstyle{phase} = [draw,fill,shape=circle,minimum size=5pt,inner sep=0pt]
    \matrix[row sep=0.4cm, column sep=0.4cm] (circuit) {
    
    ## Generate each row:
    % for i in range(qubit_num):
        \node (q${i}) {$q_1$}; &[-0.1cm]
        % for j in range(i, len(operator_list), qubit_num):
        \node[paulicomponent] (H${j}) {${operator_list[j]}}; &
        %endfor 
        \coordinate (end${i}); \\\

    % endfor
        [-0.3cm]
        ##
        ## Phase labelling:
        ##
        \node (op_angle_begin) {}; &
    % for phase_label in phase_list:
        \node[paulicomponent] {${phase_label}}; &
    %endfor
        \coordinate (op_angle_end); \\\

    };

    ## Drawing borders for each Pauli operation:
    % for k in range(0, len(operator_list), qubit_num):
    \draw (H${k}.north east) rectangle (H${(k+qubit_num-1)}.south west);
    % endfor 
    
    ## Drawing circuit lines: 
    \begin{pgfonlayer}{background}
        \draw[thick]
        % for i in range(qubit_num): 
        (q${i}) -- (end${i})
        % endfor
        ;
    \end{pgfonlayer}
    
\end{tikzpicture}
\end{document}