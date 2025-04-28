from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from schemas import missing_domain_parser



psychometric_analysis_prompt = PromptTemplate(
    template="""
    You are an expert psychologist specializing in employee behavior analysis through psychometric evaluations. Your task is to provide a concise, professional assessment focusing strictly on behavioral patterns based on the provided scores. Your analysis should be neutral and insightful .


### Domain Definitions
    **Teamwork**
    - **Ability to work with others**: Collaboration and group task preference
      (Strength) may collaborate well with colleagues
      (Development_area) may prefer to work on individual tasks rather than teams

    - **Helping others**: Support and assistance to colleagues
      (Strength) may display helpful attitude towards others
      (Development_area) may not be helpful towards colleagues


    **Emotional Stability**
    - **Emotional composure**: Assesses an individual's ability to maintain emotional composure during stressful or challenging situations. It involves managing emotions without becoming overly reactive or allowing emotions to negatively affect behaviour.
      (Strength) may maintain emotional composure in challenging situations
      (Development_area) may struggle to maintain composure

    - **Insightfulness**: Understanding self and others' emotions
      (Strength) Holds adequate emotional insight
      Development_area) has inadequate emotional insight

    - **Emotional management**: Assesses an individual's ability to manage their emotions, avoid impulsive decisions, and refrain from negatively comparing themselves to others' achievements.
      (Strength) effectively manages their emotions
      (Development_area) struggles to manage their emotions

    - **Passive aggression**: Assesses the individual’s tendency to express negative feelings indirectly through behaviors, such as shutting others out when angry, using sarcasm and lack of cooperation instead of direct communication or confrontation.
      (Strength) effective expression of emotions
      (Development_area) may express their emotions passively rather than direct communication

    - **Problem-solving**: Handling challenges effectively
      (Strength) may display problem solving attitude
      (Development_area) inadequate problem-solving skills

    - **Patience**: Assesses an individual's ability to remain calm in situations that involve delays
      (Strength) may display high level of patience
      (Development_area) may have inadequate level of patience



    **Organizational Values**
    - **Dutifulness**: Dutifulness measures an individual's sense of responsibility, commitment to completing tasks on time, attention to detail, and ensuring tasks are done thoroughly and correctly.
      (Strength) may perform their tasks with high sense of responsibility
      (Development_area) May procrastinate on tasks

    - **Moral Obligation**: It measures an individual's sense of responsibility and moral commitment to the organization
      (Strength) may commit to the best interest of the organization they serve
      (Development_area) may show inadequate commitment to the organization


    **Organizational Ethics**
    - **Moral values**: Ethical behavior and honesty
      (Strength) may follow and ethical code of conduct
      (Development_area) may not strictly follow an ethical code of conduct

    - **Fairness**: Show impartial behaviour towards others
      (Strength) show fairness in demeanour regardless of others’ age


    **Openness**
    - **Openness to limitations**: Accepting mistakes and criticism
      (Strength) may acknowledge their limitations and accept criticism
      (Development_area) may struggle to accept criticism OR acknowledge their limitations

    - **Openness to growth**: Feedback reception and adaptation
      (Strength) has potential for self-growth
      (Development_area) may struggle with self-growth
    - **Openness to individuality**: Accepting diverse perspectives
      (Strength) -accepting towards diverse temperaments
      (Development_area) may struggle to accept different temperaments
    - **Openness to new experiences**: Embracing change
      (Strength) may adapt well to change
      (Development_area) may struggle to adapt to change

    ### Language Requirements
    - Use neutral and descriptive language.
    - Avoid terms such as **"lacks," "struggles," or "deficient", "strong", "overall"**.
    - Avoid using **psychology jargon**.


    **Think step by step**

    **Provide 2-3 sentences** that:
    - explicitly identify each **strengths** and **development area** mentioned.
    - Strictly adhere to the provided Domain Definitions and  while writing the analysis
    - Refer to the provided guidelines for writing the analysis of each strength and development area. Ensure that the description aligns with the specified instructions for strengths and development areas, using the designated wording and structure. Maintain consistency in phrasing and adhere strictly to the defined approach for describing behavioral traits
    - Identify correlated domains in the given analysis using the provided correlated domain mapping.
    - Discussed co-related domains togehter
    - While writting **Helping others** do not say**"may demonstrate a strong ability"** instead use  **"may exhibit"**.
    - Use **clear** and **simple word** and proper **sentence structure**.
    - Refrain from using word **strong** in the analysis.
    - Negative words are to be avoided e.g **may not**, **limitted ability**, **unable to**, **may not always** instead use neutral sentences such as **may find it challenging** , **may struggle to display**
    - If a domain has correlated domains, incorporate insights from both to provide a more comprehensive analysis of the user’s behavior.
    - While writing your analysis, do not explicitly mention the **domain and sub domain names**; instead, describe the behaviors associated with them.
    - Provide only behavioral analysis without making evaluative judgments, such as stating overall potential or effectiveness
        **avoid phrases like 'Overall, he may show potential for effective teamwork, emotional stability, and organizational commitment**.
    - **Strengths (80-100%)** are postive traits  should be highlighted using terms like "may demonstrates," "may display","may hold" or "may have understanding",
    - **Development areas (<=60%)** are traits which needs improvement  should be described with neutral phrasing such as "may not exhibit", "may struggle", "may find it challenging" or "may hesitate"
    - Do not state that a high score in a correlated domain compensates for a lower-scoring domain. Instead, integrate insights as follows:
      - *"The individual holds adequate moral values (adequate score on moral values), yet they may not feel obligated to perform in the best interest of the organization (suggesting a low score on moral obligation)."*
    - Do not mention specific scores in the analysis, and refrain from providing **suggestions for improvement** **only present the behavioral analysis**.
    - Do no summarizing the candidate’s general behavior or personality as a wholeOnly discuss the strength and development area wihtout mentioning **overall behaviour** at the end of the analysis
    - Use "Composure" word only for **Emotional_Composure** Do not use it to for **Patience**. 

    ### Example Analyses

    **Example 1:**
    **Scores** = 'Development areas': 'name': 'Emotional Management', 'score': 40,
              'Strengths': ['name': 'Teamwork', 'score': 84,
                'name': 'PASSIVE AGGRESSION', 'score': 86,
                'name': 'PATIENCE', 'score': 80,
                'name': 'Organizational Values', 'score': 88.89,
                'name': 'MORAL VALUES', 'score': 80]
    **Analysis** = The individual may demonstrate a calm and patient demeanor, showing the ability to tolerate delays, can express their emotions effectively  and maintain composure without becoming easily frustrated or angry. He is likely to work well with diverse team members and adapt to different environments. However, he may have limited insight into his own emotions and those of others, which may lead to difficulties in handling unforeseen situations and occasionally result in impulsive decision-making under stress.
    **Example 2:**
    **Scores** = 'Development areas': [],
                  'Strengths': ['name': 'INSIGHTFULNESS', 'score': 86.67,
                    'name': 'PATIENCE', 'score': 90.0,
                    'name': 'Emotional Composure', 'score': 90.0,
                    'name': 'Emotional Management', 'score': 90.0,
                    'name': 'Emotional Stability', 'score': 92.94,
                    'name': 'Organizational Values', 'score': 93.33,
                    'name': 'OPENNESS TO GROWTH', 'score': 92.0,
                    'name': 'OPENNESS TO LIMITATIONS', 'score': 93.33,
                    'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 90.0,
                    'name': 'Openness', 'score': 92.73]
    **Analysis** = The individual seems to have adequate strengths in almost all domains. He seems to have a good grasp over his emotions and may perform well in teams. He may be open to change and diversity among others as well as accepting of his shortcomings. However, the high scores may be attributable to a general tendency to present oneself in a favorable way. The individual needs to be assessed for social desirability during the interview.
    **Example 3:**
    **Scores** = 'Development areas': [],
              'Strengths': ['name': 'Teamwork', 'score': 88,
                'name': 'PASSIVE AGGRESSION', 'score': 83.33,
                'name': 'PROBLEM-SOLVING', 'score': 90,
                'name': 'Emotional Stability', 'score': 84.71,
                'name': 'Organizational Values', 'score': 82.22,
                'name': 'Organizational Ethics', 'score': 86.67,
                'name': 'OPENNESS TO GROWTH', 'score': 92,
                'name': 'OPENNESS TO LIMITATIONS', 'score': 93.33,
                'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 90,
                'name': 'Openness', 'score': 92.73]
    **Analysis** = The individual demonstrates an open and growth-oriented mindset and can effectively express their emotion. He is accepting of individual differences and may collaborate well with people of varying temperaments. He acknowledges his limitations and accepts criticism constructively, which reflects his willingness to improve and continually work on his development. Further assessment during the interview is recommended to explore potential areas for improvement.
    **Example 4:**
    **Scores** = 'Development areas': [],
              'Strengths': ['name': 'PASSIVE AGGRESSION', 'score': 90,
                'name': 'PROBLEM-SOLVING', 'score': 90,
                'name': 'SELF-REGULATION', 'score': 90,
                'name': 'Emotional Stability', 'score': 87.06,
                'name': 'MORAL VALUES', 'score': 84,
                'name': 'OPENNESS TO GROWTH', 'score': 88,
                'name': 'Openness', 'score': 87.27]
    **Analysis** = The individual seems to be highly adaptable and accepting of individual differences, which reflects in his ability to work in collaboration with others. He may display high patience under stressful situations on account of excellent emotional management skills and approach difficulties with a problem-solving attitude. Moreover, he can express his emotion effectively and he may perform his duties with a high sense of responsibility and commitment. He seems to have a  potential for self-growth. There are no apparent areas of weakness in the profile. Therefore, the candidate needs to be assessed for social desirability or weaknesses (if any) during the interview.
    **Example 5:**
    **Scores** = 'Development areas': ['name': 'PATIENCE', 'score': 50],
                'Strengths': ['name': 'Teamwork', 'score': 84,
                  'name': 'INSIGHTFULNESS', 'score': 86.67,
                  'name': 'SELF-CONTROL', 'score': 80,
                  'name': 'SELF-REGULATION', 'score': 80,
                  'name': 'MORAL VALUES', 'score': 80,
                  'name': 'OPENNESS TO INDIVIDUALITY', 'score': 80,
                  'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 80]
    **Analysis** = The individual demonstrates an understanding of her own emotions and those of others. She may maintain composure under stress and identify multiple ways to overcome any challenge. She may interact effectively with people of varying energy levels and adapt easily to change, recognizing the importance of personal growth. While generally dutiful, she may at times prioritize efficiency over strict adherence to rules.
    **Example 6:**
    *Scores** = 'Development areas': ['name': 'Emotional Management', 'score': 60,
                'name': 'FAIRNESS', 'score': 60,
                'name': 'OPENNESS TO LIMITATIONS', 'score': 60],
              'Strengths': ['name': 'PATIENCE', 'score': 80,
                'name': 'PROBLEM-SOLVING', 'score': 80,
                'name': 'Emotional Composure', 'score': 80,
                'name': 'Organizational Values', 'score': 84.44,
                'name': 'MORAL VALUES', 'score': 80,
                'name': 'OPENNESS TO INDIVIDUALITY', 'score': 80,
                'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 80]
    **Analysis** = The individual seems to be adaptable, responsible, and accepting of individual differences. She may hold  moral values reflecting in commitment towards the organization. She may find it challenging to regulate her emotions; however, she may maintain her composure. Moreover, she may find it difficult to acknowledge her shortcomings or may not accept criticism.
    **Example 7:**
    **Scores** = 'Development areas': ['name': 'Emotional Composure', 'score': 60,
                    'name': 'DUTIFULNESS', 'score': 60,
                    'name': 'FAIRNESS', 'score': 60,
                    'name': 'OPENNESS TO LIMITATIONS', 'score': 46.67],
                  'Strengths': ['name': 'Teamwork', 'score': 80,
                    'name': 'INSIGHTFULNESS', 'score': 80,
                    'name': 'PATIENCE', 'score': 80,
                    'name': 'PROBLEM-SOLVING', 'score': 80,
                    'name': 'Emotional Management', 'score': 80,
                    'name': 'MORAL VALUES', 'score': 80,
                    'name': 'OPENNESS TO INDIVIDUALITY', 'score': 80,
                    'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 80]
    **Analysis** = The individual may display high patience and adequate insight into his emotions. However, he may lose composure when faced with difficulties. He seems to procrastinate with respect to his tasks on hands; reflecting in a relatively inadequate sense of responsibility. Yet, the candidate have good set of moral values and may demonstrate a sense of commitment towards the organization. Moreover, he may struggle to accept criticism or acknowledge his shortcomings

    Now analyze the following scores:
- **Strengths:** {strength}
- **Development Areas:** {development_area}

""",
    input_variables=["strength", "development_area"],
)


conflicted_item_prompt = PromptTemplate(
    template="""
    You are an expert in psychometric evaluation and behavioral analysis. Your task is to validate a given psychometric analysis by checking whether the strengths and development areas identified align with the user's responses to the provided questions.
    ### Domain Definitions
    **Teamwork**
    - **Ability to work with others**: Collaboration and group task preference
      (High) may collaborate well with colleagues
      (Low) may prefer to work on individual tasks rather than teams
      Correlation with Openness to individuality
    - **Helping others**: Support and assistance to colleagues
      (High) may display helpful attitude towards others
      (Low) may not be helpful towards colleagues


    **Emotional Stability**
    - **Emotional composure**: Maintaining composure under stress
      (High) may maintain emotional composure in challenging situations
      (Low) may struggle to maintain composure
      Correlation with Insightfulness, patience, & emotional management
    - **Insightfulness**: Understanding self and others' emotions
      (High) Holds adequate emotional insight
      (Low) has inadequate emotional insight
      Correlation with self-control, patience, passive aggression & emotional management
    - **Emotional management**: Managing emotions
      (High) effectively manages their emotions
      (Low) struggles to manage their emotions
      Correlation with self-control, patience, passive aggression & insightfulness)
    - **Passive aggression**: Indirect expression of negative feelings
      (High) effective expression of emotions
      (Low) may express their emotions passively rather than direct communication
      Correlation with Insightfulness, patience, emotional composure, and emotional management)
    - **Problem-solving**: Handling challenges effectively
      (High) may display problem solving attitude
      (Low) inadequate problem-solving skills
      Correlation with openness to new experiences and other sub-domains of Emotional Stability
    - **Patience**: Calmness during delays
      (High) may display high level of patience
      (Low) may have inadequate level of patience
      Correlation with Insightfulness, emotional composure, and emotional management


    **Organizational Values**
    - **Dutifulness**: Thorough and timely task completion
      (High) may perform their tasks with high sense of responsibility
      (Low) May procrastinate on tasks
      Correlation with moral values, and moral obligation)
    - **Moral Obligation**: Alignment with organizational goals
      (High) may commit to the best interest of the organization they serve
      (Low) may show inadequate commitment to the organization
      Correlation with moral values, fairness and dutifulness

    **Organizational Ethics**
    - **Moral values**: Ethical behavior and honesty
      (High) may follow and ethical code of conduct
      (Low) may not strictly follow an ethical code of conduct
      Correlation with moral obligation, fairness and dutifulness
    - **Fairness**: Show impartial behaviour towards others
      (High) show fairness in demeanour regardless of others’ age


    **Openness**
    - **Openness to limitations**: Accepting mistakes and criticism
      (High) may acknowledge their limitations and accept criticism
      (Low) may struggle to accept criticism OR acknowledge their limitations
      Correlation with Openness to growth
    - **Openness to growth**: Feedback reception and adaptation
      (High) has potential for self-growth
      (Low) may struggle with self-growth
      Correlation with openness to limitation, openness to new experiences, and openness to individuality
    - **Openness to individuality**: Accepting diverse perspectives
      (High) -accepting towards diverse temperaments
      (Low) may struggle to accept different temperaments
      Correlation with teamwork
    - **Openness to new experiences**: Embracing change
      (High) may adapt well to change
      (Low) may struggle to adapt to change
      Correlation with problem solving skills, openness to individuality, growth mindset

    ###Question and their option selected by user
    - You will be provided with a list of questions and the options selected by the user.
    - Every trait has multiple questions which are representing certain behaviour
    - The dataset contains two types of questions:
          Forward Questions (standard scoring).
          Reverse Questions (R) (where interpretation is reversed).
    - Ensure that you correctly interpret the responses based on their respective types (forward or reverse).
    - Your analysis should be based only on the provided user selections without making assumptions beyond the given data.
    - Below is the user’s collected data:

    ## Instructions
    Verify the Justification of Strengths and Development Areas:
        Check if the strengths and development areas identified in the psychometric analysis are supported by the user’s responses.
        For every domain consider all the user answer of the user before validating that domain
        For reverser question with **(R)** scoring is reversed
        Ensure that each identified trait correlates logically with the selected answers.

    Identify Missing or Misaligned Aspects:

        Highlight if any key strength or development area is missing based on the user's responses.
        Flag any inconsistencies where the analysis does not accurately reflect the user's selected options.

    ###Output
    - Return only the conflicting area
**user_data:** {user_data}
**Analysis:** {analysis}


""",
    input_variables=["user_data","analysis"],
)



item_analysis_1_prompt = PromptTemplate(
    template="""
    You are an expert psychologist specializing in employee behavior analysis through psychometric evaluations. Your task is to provide a concise, professional assessment focusing strictly on behavioral patterns based on the provided data. Your analysis should be neutral, descriptive, and insightful while maintaining a professional tone.


    ### Domain Definitions
    **Teamwork**
    - **Ability to work with others**: Collaboration and group task preference
      (High) may collaborate well with colleagues
      (Low) may prefer to work on individual tasks rather than teams
      Correlation with Openness to individuality
    - **Helping others**: Support and assistance to colleagues
      (High) may display helpful attitude towards others
      (Low) may not be helpful towards colleagues


    **Emotional Stability**
    - **Emotional composure**: Maintaining composure under stress
      (High) may maintain emotional composure in challenging situations
      (Low) may struggle to maintain composure
      Correlation with Insightfulness, patience, & emotional management
    - **Insightfulness**: Understanding self and others' emotions
      (High) Holds adequate emotional insight
      (Low) has inadequate emotional insight
      Correlation with self-control, patience, passive aggression & emotional management
    - **Emotional management**: Managing emotions
      (High) effectively manages their emotions
      (Low) struggles to manage their emotions
      Correlation with self-control, patience, passive aggression & insightfulness)
    - **Passive aggression**: Indirect expression of negative feelings
      (High) effective expression of emotions
      (Low) may express their emotions passively rather than direct communication
      Correlation with Insightfulness, patience, emotional composure, and emotional management)
    - **Problem-solving**: Handling challenges effectively
      (High) may display problem solving attitude
      (Low) inadequate problem-solving skills
      Correlation with openness to new experiences and other sub-domains of Emotional Stability
    - **Patience**: Calmness during delays
      (High) may display high level of patience
      (Low) may have inadequate level of patience
      Correlation with Insightfulness, emotional composure, and emotional management


    **Organizational Values**
    - **Dutifulness**: Thorough and timely task completion
      (High) may perform their tasks with high sense of responsibility
      (Low) May procrastinate on tasks
      Correlation with moral values, and moral obligation)
    - **Moral Obligation**: Alignment with organizational goals
      (High) may commit to the best interest of the organization they serve
      (Low) may show inadequate commitment to the organization
      Correlation with moral values, fairness and dutifulness

    **Organizational Ethics**
    - **Moral values**: Ethical behavior and honesty
      (High) may follow and ethical code of conduct
      (Low) may not strictly follow an ethical code of conduct
      Correlation with moral obligation, fairness and dutifulness
    - **Fairness**: Show impartial behaviour towards others
      (High) show fairness in demeanour regardless of others’ age


    **Openness**
    - **Openness to limitations**: Accepting mistakes and criticism
      (High) may acknowledge their limitations and accept criticism
      (Low) may struggle to accept criticism OR acknowledge their limitations
      Correlation with Openness to growth
    - **Openness to growth**: Feedback reception and adaptation
      (High) has potential for self-growth
      (Low) may struggle with self-growth
      Correlation with openness to limitation, openness to new experiences, and openness to individuality
    - **Openness to individuality**: Accepting diverse perspectives
      (High) -accepting towards diverse temperaments
      (Low) may struggle to accept different temperaments
      
    - **Openness to new experiences**: Embracing change
      (High) may adapt well to change
      (Low) may struggle to adapt to change
      

    ###Question and their option selected by user
    - You will be provided with a list of questions and the options selected by the user.
    - Every trait has multiple questions which are representing certain behaviour
    - The dataset contains two types of questions:
          Forward Questions (standard scoring).
          Reverse Questions (R) (where interpretation is reversed).
    - Ensure that you correctly interpret the responses based on their respective types (forward or reverse).
    - Your analysis should be based only on the provided user selections without making assumptions beyond the given data.
    - Below is the user’s collected data:
      **user_data:** {user_data}

    ### Language Requirements
    - Use neutral and descriptive language.
    - Avoid terms such as **"lacks," "struggles," or "deficient", "strong", "overall"**.
    - Avoid using **psychology jargon**.


    **Think step by step**
    - i Will provide you with user data and you have to write analysis based on user answer,
    - For every trait thoroughly think about all user answer and then make a statement
    - explicitly identify each **strengths** and **development area** mentioned.
    - Strictly adhere to the provided Domain Definitions while writing the analysis
    - Identify correlated domains in the given analysis using the provided correlated domain mapping.
    - Discussed co-related domains togehter
    - While writting **Helping others** do not say**"may demonstrate a strong ability"** instead use  **"may exhibit"**.
    - Use **clear** and **simple word** and proper **sentence structure**.
    - Refrain from using word **strong** in the analysis.
    - Negative words are to be avoided e.g **may not**, **limitted ability**, **unble to**, **may not always** instead use neutral sentences such as **may find it challenging** , **may struggle to display**
    - If a domain has correlated domains, incorporate insights from both to provide a more comprehensive analysis of the user’s behavior.
    - While writing your analysis, do not explicitly mention the **domain and sub domain names**; instead, describe the behaviors associated with them.
    - Provide only behavioral analysis without making evaluative judgments, such as stating overall potential or effectiveness
        **avoid phrases like 'Overall, he may show potential for effective teamwork, emotional stability, and organizational commitment**.
    - **Strengths** are postive traits  should be highlighted using terms like "may demonstrates," "may display","may hold" or "may have understanding",
    - **Development areas** are traits which needs improvement  should be described with neutral phrasing such as "may not exhibit", "may struggle", "may find it challenging" or "may hesitate"
    - **Correlated domains should be referenced naturally where relevant to provide a holistic understanding of behavioral tendencies**.
    - Do not state that a high score in a correlated domain compensates for a lower-scoring domain. Instead, integrate insights as follows:
      - *"The individual holds adequate moral values (adequate score on moral values), yet they may not feel obligated to perform in the best interest of the organization (suggesting a low score on moral obligation)."*
    - Do not mention specific scores in the analysis, and refrain from providing **suggestions for improvement** **only present the behavioral analysis**.


    ### Example Analyses

    **Example 1:**
    **Analysis** = The individual may demonstrate a calm and patient demeanor, showing the ability to tolerate delays and maintain composure without becoming easily frustrated or angry. He is likely to work well with diverse team members and adapt to different environments. However, he may have limited insight into his own emotions and those of others, which may lead to difficulties in handling unforeseen situations and occasionally result in impulsive decision-making under stress.
    **Example 2:**

    **Analysis** = The individual seems to have adequate strengths in almost all domains. He seems to have a good grasp over his emotions and may perform well in teams. He may be open to change and diversity among others as well as accepting of his shortcomings. However, the high scores may be attributable to a general tendency to present oneself in a favorable way. The individual needs to be assessed for social desirability during the interview.
    **Example 3:**

    **Analysis** = The individual demonstrates an open and growth-oriented mindset. He is accepting of individual differences and may collaborate well with people of varying temperaments. He acknowledges his limitations and accepts criticism constructively, which reflects his willingness to improve and continually work on his development. Further assessment during the interview is recommended to explore potential areas for improvement.
    **Example 4:**

    **Analysis** = The individual seems to be highly adaptable and accepting of individual differences, which reflects in his ability to work in collaboration with others. He may display high patience under stressful situations on account of excellent emotional management skills and approach difficulties with a problem-solving attitude. Moreover, he may perform his duties with a high sense of responsibility and commitment. He seems to have a  potential for self-growth. There are no apparent areas of weakness in the profile. Therefore, the candidate needs to be assessed for social desirability or weaknesses (if any) during the interview.
    **Example 5:**

    **Analysis** = The individual demonstrates an understanding of her own emotions and those of others. She may maintain composure under stress and identify multiple ways to overcome any challenge. She may interact effectively with people of varying energy levels and adapt easily to change, recognizing the importance of personal growth. While generally dutiful, she may at times prioritize efficiency over strict adherence to rules.
    **Example 6:**

    **Analysis** = The individual seems to be adaptable, responsible, and accepting of individual differences. She may hold  moral values reflecting in commitment towards the organization. She may find it challenging to regulate her emotions; however, she may maintain her composure. Moreover, she may find it difficult to acknowledge her shortcomings or may not accept criticism.
    **Example 7:**

    **Analysis** = The individual may display high patience and adequate insight into his emotions. However, he may lose composure when faced with difficulties. He seems to procrastinate with respect to his tasks on hands; reflecting in a relatively inadequate sense of responsibility. Yet, the candidate have good set of moral values and may demonstrate a sense of commitment towards the organization. Moreover, he may struggle to accept criticism or acknowledge his shortcomings



""",
    input_variables=["user_data"],
)

item_analysis_2_prompt = PromptTemplate(
    template="""
    You are an expert psychologist specializing in employee behavior analysis through psychometric evaluations. Your task is to provide a concise, professional assessment focusing strictly on behavioral patterns based on the provided scores. Your analysis should be neutral, descriptive, and insightful while maintaining a professional tone.


    ### Domain Definitions
    **Teamwork**
    - **Ability to work with others**: Collaboration and group task preference
      (Strength) may collaborate well with colleagues
      (Development_area) may prefer to work on individual tasks rather than teams

    - **Helping others**: Support and assistance to colleagues
      (Strength) may display helpful attitude towards others
      (Development_area) may not be helpful towards colleagues


    **Emotional Stability**
    - **Emotional composure**: Assesses an individual's ability to maintain emotional composure during stressful or challenging situations. It involves managing emotions without becoming overly reactive or allowing emotions to negatively affect behaviour.
      (Strength) may maintain emotional composure in challenging situations
      (Development_area) may struggle to maintain composure

    - **Insightfulness**: Understanding self and others' emotions
      (Strength) Holds adequate emotional insight
      Development_area) has inadequate emotional insight

    - **Emotional management**: Assesses an individual's ability to manage their emotions, avoid impulsive decisions, and refrain from negatively comparing themselves to others' achievements.
      (Strength) effectively manages their emotions
      (Development_area) struggles to manage their emotions

    - **Passive aggression**: Assesses the individual’s tendency to express negative feelings indirectly through behaviors, such as shutting others out when angry, using sarcasm and lack of cooperation instead of direct communication or confrontation.
      (Strength) effective expression of emotions
      (Development_area) may express their emotions passively rather than direct communication

    - **Problem-solving**: Handling challenges effectively
      (Strength) may display problem solving attitude
      (Development_area) inadequate problem-solving skills

    - **Patience**: Assesses an individual's ability to remain calm in situations that involve delays
      (Strength) may display high level of patience
      (Development_area) may have inadequate level of patience

    **Organizational Values**
    - **Dutifulness**: Dutifulness measures an individual's sense of responsibility, commitment to completing tasks on time, attention to detail, and ensuring tasks are done thoroughly and correctly.
      (Strength) may perform their tasks with high sense of responsibility
      (Development_area) May procrastinate on tasks

    - **Moral Obligation**: It measures an individual's sense of responsibility and moral commitment to the organization
      (Strength) may commit to the best interest of the organization they serve
      (Development_area) may show inadequate commitment to the organization

    **Organizational Ethics**
    - **Moral values**: Ethical behavior and honesty
      (Strength) may follow and ethical code of conduct
      (Development_area) may not strictly follow an ethical code of conduct

    - **Fairness**: Show impartial behaviour towards others
      (Strength) show fairness in demeanour regardless of others’ age

    **Openness**
    - **Openness to limitations**: Accepting mistakes and criticism
      (Strength) may acknowledge their limitations and accept criticism
      (Development_area) may struggle to accept criticism OR acknowledge their limitations

    - **Openness to growth**: Feedback reception and adaptation
      (Strength) has potential for self-growth
      (Development_area) may struggle with self-growth
    - **Openness to individuality**: Accepting diverse perspectives
      (Strength) -accepting towards diverse temperaments
      (Development_area) may struggle to accept different temperaments
    - **Openness to new experiences**: Embracing change
      (Strength) may adapt well to change
      (Development_area) may struggle to adapt to change

    ###Question and their option selected by user
    - You will be provided with a list of questions and the options selected by the user.
    - Every trait has multiple questions which are representing certain behaviour
    - The dataset contains two types of questions:
          Forward Questions (standard scoring).
          Reverse Questions (R) (where interpretation is reversed).
    - Ensure that you correctly interpret the responses based on their respective types (forward or reverse).
    - Your analysis should be based only on the provided user selections without making assumptions beyond the given data.
    - Below is the user’s collected data:
      **user_data:** {user_data}

    ### Language Requirements
    - Use neutral and descriptive language.
    - Avoid terms such as **"lacks," "struggles," or "deficient", "strong", "overall"**.
    - Avoid using **psychology jargon**.


    **Think step by step**
    **Provide 2-3 sentences** that:
    - explicitly identify each **strengths** and **development area** mentioned.
    - Strictly adhere to the provided Domain Definitions while writing the analysis
    - Identify correlated domains in the given analysis using the provided correlated domain mapping.
    - Discussed co-related domains togehter
    - While writting **Helping others** do not say**"may demonstrate a strong ability"** instead use  **"may exhibit"**.
    - Use **clear** and **simple word** and proper **sentence structure**.
    - Refrain from using word **strong** in the analysis.
    - Negative words are to be avoided e.g **may not**, **limitted ability**, **unble to**, **may not always** instead use neutral sentences such as **may find it challenging** , **may struggle to display**
    - If a domain has correlated domains, incorporate insights from both to provide a more comprehensive analysis of the user’s behavior.
    - While writing your analysis, do not explicitly mention the **domain and sub domain names**; instead, describe the behaviors associated with them.
    - Provide only behavioral analysis without making evaluative judgments, such as stating overall potential or effectiveness
        **avoid phrases like 'Overall, he may show potential for effective teamwork, emotional stability, and organizational commitment**.
    - **Strengths (80-100%)** are postive traits  should be highlighted using terms like "may demonstrates," "may display","may hold" or "may have understanding",
    - **Development areas (<=60%)** are traits which needs improvement  should be described with neutral phrasing such as "may not exhibit", "may struggle", "may find it challenging" or "may hesitate"
    - **Correlated domains should be referenced naturally where relevant to provide a holistic understanding of behavioral tendencies**.
    - Do not state that a high score in a correlated domain compensates for a lower-scoring domain. Instead, integrate insights as follows:
      - *"The individual holds adequate moral values (adequate score on moral values), yet they may not feel obligated to perform in the best interest of the organization (suggesting a low score on moral obligation)."*
    - Do not mention specific scores in the analysis, and refrain from providing **suggestions for improvement** **only present the behavioral analysis**.
    - I have provided the user data which contain user pscychometric answers and you have to take them into account for writting more comprehensive analysis


    ### Example Analyses

    **Example 1:**
    **Scores** = 'Development areas': 'name': 'Emotional Management', 'score': 40,
              'Strengths': ['name': 'Teamwork', 'score': 84,
                'name': 'PASSIVE AGGRESSION', 'score': 86,
                'name': 'PATIENCE', 'score': 80,
                'name': 'Organizational Values', 'score': 88.89,
                'name': 'MORAL VALUES', 'score': 80]
    **Analysis** = The individual may demonstrate a calm and patient demeanor, showing the ability to tolerate delays and maintain composure without becoming easily frustrated or angry. He is likely to work well with diverse team members and adapt to different environments. However, he may have limited insight into his own emotions and those of others, which may lead to difficulties in handling unforeseen situations and occasionally result in impulsive decision-making under stress.
    **Example 2:**
    **Scores** = 'Development areas': [],
                  'Strengths': ['name': 'INSIGHTFULNESS', 'score': 86.67,
                    'name': 'PATIENCE', 'score': 90.0,
                    'name': 'Emotional Composure', 'score': 90.0,
                    'name': 'Emotional Management', 'score': 90.0,
                    'name': 'Emotional Stability', 'score': 92.94,
                    'name': 'Organizational Values', 'score': 93.33,
                    'name': 'OPENNESS TO GROWTH', 'score': 92.0,
                    'name': 'OPENNESS TO LIMITATIONS', 'score': 93.33,
                    'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 90.0,
                    'name': 'Openness', 'score': 92.73]
    **Analysis** = The individual seems to have adequate strengths in almost all domains. He seems to have a good grasp over his emotions and may perform well in teams. He may be open to change and diversity among others as well as accepting of his shortcomings. However, the high scores may be attributable to a general tendency to present oneself in a favorable way. The individual needs to be assessed for social desirability during the interview.
    **Example 3:**
    **Scores** = 'Development areas': [],
              'Strengths': ['name': 'Teamwork', 'score': 88,
                'name': 'PASSIVE AGGRESSION', 'score': 83.33,
                'name': 'PROBLEM-SOLVING', 'score': 90,
                'name': 'Emotional Stability', 'score': 84.71,
                'name': 'Organizational Values', 'score': 82.22,
                'name': 'Organizational Ethics', 'score': 86.67,
                'name': 'OPENNESS TO GROWTH', 'score': 92,
                'name': 'OPENNESS TO LIMITATIONS', 'score': 93.33,
                'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 90,
                'name': 'Openness', 'score': 92.73]
    **Analysis** = The individual demonstrates an open and growth-oriented mindset. He is accepting of individual differences and may collaborate well with people of varying temperaments. He acknowledges his limitations and accepts criticism constructively, which reflects his willingness to improve and continually work on his development. Further assessment during the interview is recommended to explore potential areas for improvement.
    **Example 4:**
    **Scores** = 'Development areas': [],
              'Strengths': ['name': 'PASSIVE AGGRESSION', 'score': 90,
                'name': 'PROBLEM-SOLVING', 'score': 90,
                'name': 'SELF-REGULATION', 'score': 90,
                'name': 'Emotional Stability', 'score': 87.06,
                'name': 'MORAL VALUES', 'score': 84,
                'name': 'OPENNESS TO GROWTH', 'score': 88,
                'name': 'Openness', 'score': 87.27]
    **Analysis** = The individual seems to be highly adaptable and accepting of individual differences, which reflects in his ability to work in collaboration with others. He may display high patience under stressful situations on account of excellent emotional management skills and approach difficulties with a problem-solving attitude. Moreover, he may perform his duties with a high sense of responsibility and commitment. He seems to have a  potential for self-growth. There are no apparent areas of weakness in the profile. Therefore, the candidate needs to be assessed for social desirability or weaknesses (if any) during the interview.
    **Example 5:**
    **Scores** = 'Development areas': ['name': 'PATIENCE', 'score': 50],
                'Strengths': ['name': 'Teamwork', 'score': 84,
                  'name': 'INSIGHTFULNESS', 'score': 86.67,
                  'name': 'SELF-CONTROL', 'score': 80,
                  'name': 'SELF-REGULATION', 'score': 80,
                  'name': 'MORAL VALUES', 'score': 80,
                  'name': 'OPENNESS TO INDIVIDUALITY', 'score': 80,
                  'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 80]
    **Analysis** = The individual demonstrates an understanding of her own emotions and those of others. She may maintain composure under stress and identify multiple ways to overcome any challenge. She may interact effectively with people of varying energy levels and adapt easily to change, recognizing the importance of personal growth. While generally dutiful, she may at times prioritize efficiency over strict adherence to rules.
    **Example 6:**
    *Scores** = 'Development areas': ['name': 'Emotional Management', 'score': 60,
                'name': 'FAIRNESS', 'score': 60,
                'name': 'OPENNESS TO LIMITATIONS', 'score': 60],
              'Strengths': ['name': 'PATIENCE', 'score': 80,
                'name': 'PROBLEM-SOLVING', 'score': 80,
                'name': 'Emotional Composure', 'score': 80,
                'name': 'Organizational Values', 'score': 84.44,
                'name': 'MORAL VALUES', 'score': 80,
                'name': 'OPENNESS TO INDIVIDUALITY', 'score': 80,
                'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 80]
    **Analysis** = The individual seems to be adaptable, responsible, and accepting of individual differences. She may hold  moral values reflecting in commitment towards the organization. She may find it challenging to regulate her emotions; however, she may maintain her composure. Moreover, she may find it difficult to acknowledge her shortcomings or may not accept criticism.
    **Example 7:**
    **Scores** = 'Development areas': ['name': 'Emotional Composure', 'score': 60,
                    'name': 'DUTIFULNESS', 'score': 60,
                    'name': 'FAIRNESS', 'score': 60,
                    'name': 'OPENNESS TO LIMITATIONS', 'score': 46.67],
                  'Strengths': ['name': 'Teamwork', 'score': 80,
                    'name': 'INSIGHTFULNESS', 'score': 80,
                    'name': 'PATIENCE', 'score': 80,
                    'name': 'PROBLEM-SOLVING', 'score': 80,
                    'name': 'Emotional Management', 'score': 80,
                    'name': 'MORAL VALUES', 'score': 80,
                    'name': 'OPENNESS TO INDIVIDUALITY', 'score': 80,
                    'name': 'OPENNESS TO NEW EXPERIENCES', 'score': 80]
    **Analysis** = The individual may display high patience and adequate insight into his emotions. However, he may lose composure when faced with difficulties. He seems to procrastinate with respect to his tasks on hands; reflecting in a relatively inadequate sense of responsibility. Yet, the candidate have good set of moral values and may demonstrate a sense of commitment towards the organization. Moreover, he may struggle to accept criticism or acknowledge his shortcomings

    Now analyze the following scores:
- **Strengths:** {strength}
- **Development Areas:** {development_area}
- **User Data:** {user_data}

""",
    input_variables=["strength", "development_area", "user_data"],
)



corelated_domain_together_prompt = PromptTemplate(
    template="""You are an expert in text structuring and organization. Your task is to reorder the sentences in a psychometric analysis to group correlated domains together, without modifying the original wording or context.

### Domain Definitions
    **Teamwork**
    - **Ability to work with others**: Collaboration and group task preference
      (Strength) may collaborate well with colleagues
      (Development_area) may prefer to work on individual tasks rather than teams

    - **Helping others**: Support and assistance to colleagues
      (Strength) may display helpful attitude towards others
      (Development_area) may not be helpful towards colleagues


    **Emotional Stability**
    - **Emotional composure**: Assesses an individual's ability to maintain emotional composure during stressful or challenging situations. It involves managing emotions without becoming overly reactive or allowing emotions to negatively affect behaviour.
      (Strength) may maintain emotional composure in challenging situations
      (Development_area) may struggle to maintain composure

    - **Insightfulness**: Understanding self and others' emotions
      (Strength) Holds adequate emotional insight
      Development_area) has inadequate emotional insight

    - **Emotional management**: Assesses an individual's ability to manage their emotions, avoid impulsive decisions, and refrain from negatively comparing themselves to others' achievements.
      (Strength) effectively manages their emotions
      (Development_area) struggles to manage their emotions

    - **Passive aggression**: Assesses the individual’s tendency to express negative feelings indirectly through behaviors, such as shutting others out when angry, using sarcasm and lack of cooperation instead of direct communication or confrontation.
      (Strength) effective expression of emotions
      (Development_area) may express their emotions passively rather than direct communication

    - **Problem-solving**: Handling challenges effectively
      (Strength) may display problem solving attitude
      (Development_area) inadequate problem-solving skills

    - **Patience**: Assesses an individual's ability to remain calm in situations that involve delays
      (Strength) may display high level of patience
      (Development_area) may have inadequate level of patience



    **Organizational Values**
    - **Dutifulness**: Dutifulness measures an individual's sense of responsibility, commitment to completing tasks on time, attention to detail, and ensuring tasks are done thoroughly and correctly.
      (Strength) may perform their tasks with high sense of responsibility
      (Development_area) May procrastinate on tasks

    - **Moral Obligation**: It measures an individual's sense of responsibility and moral commitment to the organization
      (Strength) may commit to the best interest of the organization they serve
      (Development_area) may show inadequate commitment to the organization


    **Organizational Ethics**
    - **Moral values**: Ethical behavior and honesty
      (Strength) may follow and ethical code of conduct
      (Development_area) may not strictly follow an ethical code of conduct

    - **Fairness**: Show impartial behaviour towards others
      (Strength) show fairness in demeanour regardless of others’ age


    **Openness**
    - **Openness to limitations**: Accepting mistakes and criticism
      (Strength) may acknowledge their limitations and accept criticism
      (Development_area) may struggle to accept criticism OR acknowledge their limitations

    - **Openness to growth**: Feedback reception and adaptation
      (Strength) has potential for self-growth
      (Development_area) may struggle with self-growth
    - **Openness to individuality**: Accepting diverse perspectives
      (Strength) -accepting towards diverse temperaments
      (Development_area) may struggle to accept different temperaments
    - **Openness to new experiences**: Embracing change
      (Strength) may adapt well to change
      (Development_area) may struggle to adapt to change
Instructions:

    Identify Correlated Domains: Utilize the provided correlated domain mapping to determine which domains are related.
    Reorder Sentences: Adjust the sequence of sentences in the analysis to ensure that insights related to correlated domains appear consecutively.
    Preserve Original Wording: Do not add, remove, or alter any words, phrases, or sentence structures. Maintain the original context and meaning.
    Ensure Coherence: After reordering, the analysis should read naturally and maintain logical flow.
    Avoid Explicit Mention of Correlations: Do not state that certain domains are correlated or introduce any new explanations.

Output:
    It should return a paragraph


Input:

    Correlated Domains: {correlated_domains}

    Analysis: {analysis}""",
    input_variables=["analysis", "correlated_domains"]
)



missing_strengths_and_weakness_prompt = PromptTemplate(
    template="""
    You are an expert in psychometric analysis and critical evaluation. Your task is to analyze the provided strengths and weaknesses and compare them with the given analysis to identify any missing elements.
### Domain Definitions
    **Teamwork**
    - **Ability to work with others**: Collaboration and group task preference
      (Strength) may collaborate well with colleagues
      (Development_area) may prefer to work on individual tasks rather than teams

    - **Helping others**: Support and assistance to colleagues
      (Strength) may display helpful attitude towards others
      (Development_area) may not be helpful towards colleagues


    **Emotional Stability**
    - **Emotional composure**: Assesses an individual's ability to maintain emotional composure during stressful or challenging situations. It involves managing emotions without becoming overly reactive or allowing emotions to negatively affect behaviour.
      (Strength) may maintain emotional composure in challenging situations
      (Development_area) may struggle to maintain composure

    - **Insightfulness**: Understanding self and others' emotions
      (Strength) Holds adequate emotional insight
      Development_area) has inadequate emotional insight

    - **Emotional management**: Assesses an individual's ability to manage their emotions, avoid impulsive decisions, and refrain from negatively comparing themselves to others' achievements.
      (Strength) effectively manages their emotions
      (Development_area) struggles to manage their emotions

    - **Passive aggression**: Assesses the individual’s tendency to express negative feelings indirectly through behaviors, such as shutting others out when angry, using sarcasm and lack of cooperation instead of direct communication or confrontation.
      (Strength) effective expression of emotions
      (Development_area) may express their emotions passively rather than direct communication

    - **Problem-solving**: Handling challenges effectively
      (Strength) may display problem solving attitude
      (Development_area) inadequate problem-solving skills

    - **Patience**: Assesses an individual's ability to remain calm in situations that involve delays
      (Strength) may display high level of patience
      (Development_area) may have inadequate level of patience



    **Organizational Values**
    - **Dutifulness**: Dutifulness measures an individual's sense of responsibility, commitment to completing tasks on time, attention to detail, and ensuring tasks are done thoroughly and correctly.
      (Strength) may perform their tasks with high sense of responsibility
      (Development_area) May procrastinate on tasks

    - **Moral Obligation**: It measures an individual's sense of responsibility and moral commitment to the organization
      (Strength) may commit to the best interest of the organization they serve
      (Development_area) may show inadequate commitment to the organization


    **Organizational Ethics**
    - **Moral values**: Ethical behavior and honesty
      (Strength) may follow and ethical code of conduct
      (Development_area) may not strictly follow an ethical code of conduct

    - **Fairness**: Show impartial behaviour towards others
      (Strength) show fairness in demeanour regardless of others’ age


    **Openness**
    - **Openness to limitations**: Accepting mistakes and criticism
      (Strength) may acknowledge their limitations and accept criticism
      (Development_area) may struggle to accept criticism OR acknowledge their limitations

    - **Openness to growth**: Feedback reception and adaptation
      (Strength) has potential for self-growth
      (Development_area) may struggle with self-growth
    - **Openness to individuality**: Accepting diverse perspectives
      (Strength) -accepting towards diverse temperaments
      (Development_area) may struggle to accept different temperaments
    - **Openness to new experiences**: Embracing change
      (Strength) may adapt well to change
      (Development_area) may struggle to adapt to change

    Input Structure:
    - Strengths: {strengths}
    - Weaknesses: {development_area}
    - Analysis: {analysis}

    Think step by step:

    - Identify whether all the listed strengths and weaknesses are mentioned in the analysis.
    - Highlight any strengths or weaknesses that are missing from the analysis.
    - Identify any strengths or development areas that are discussed in the analysis but not explicitly listed.

    {format_instructions}
    """,
    input_variables=["strengths", "development_area", "analysis"],
    partial_variables={"format_instructions": missing_domain_parser.get_format_instructions()}  # Ensures proper JSON output
)




judge_llm_prompt = PromptTemplate(
    template="""
You are analyzing a psychometric report for two specific issues. Carefully read the analysis and perform the following checks:

1. Check if the analysis ends with an overall behavioral tendency statement (e.g., summarizing the candidate’s general behavior or personality as a whole).
2. Check if the word "composure" is used to describe traits like "patience" in the analysis, even though "Emotional Composure" is not mentioned in the strengths or weaknesses.

Your task is to return:
- "Unacceptable" if **either or both** of the issues are found in the analysis.
- "Acceptable" only if **neither** issue is present.

Input:
Analysis: {analysis}
""",
    input_variables=["analysis"],
)

format_text_prompt = PromptTemplate(
    template="""
You are provided with a paragraph describing an individual's behavioral and psychometric traits.
- Task
    Reformat the paragraph to improve clarity, structure, and readability.
    Keep the original meaning and text intact — do not infer or invent new traits.
- Output Format:
    Return the content as a well-structured paragraph that may include:
          Line breaks after however or when it start to discuss development areas
    Do not change Text only format it
    

Input:
Analysis: {analysis}
""",
    input_variables=["analysis"],
)

