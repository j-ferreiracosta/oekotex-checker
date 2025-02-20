import gradio as gr
import os
from openai_cli.cli_openai import fetch_model_choices, process_chat
from scripts.loading_files import load_files_to_json

# Retrieve the list of available models.
available_models = fetch_model_choices()
df_json = None

def toggle_panel(current_visible):
    new_visible = not current_visible
    # Update the panel's visible property.
    return new_visible, gr.update(visible=new_visible)

def clear_chat():
    return [], []


def combine_oekotex_inputs(product_text, scope_text, chat_state, model, temperature, max_tokens, top_k, system_role):
    combined_text = "<PRODUCT>" + product_text + "</PRODUCT>\n<SCOPE>" + scope_text + "</SCOPE>"
    return process_chat(combined_text, chat_state, model, temperature, max_tokens, top_k, system_role)

def start_loading_files(product_file, certification_file,chat_state,  model, temperature, max_tokens, top_k, system_role):
    global df_json
    if product_file is None or certification_file is None:
        raise gr.Error("Please upload both files")
    if not os.path.exists(product_file.name) or not os.path.exists(certification_file.name):
        raise gr.Error("Please upload both files")
    df_json = load_files_to_json(product_file_path=product_file, certification_file_path=certification_file)
    
    return process_chat(df_json, chat_state, model, temperature, max_tokens, top_k, system_role)

#############################################
# Build the Gradio interface.
#############################################
with gr.Blocks(css="""
    /* Position the options toggle button in the top-right corner */
    #toggle_btn {
        position: absolute;
        top: 10;
        right: 10px;
        z-index: 1000;
    }
               
        #options_panel {
        width: 10%;       /* Set your desired width */
        min-width: 5%;   /* Ensure it doesn't shrink */
        max-width: 20%;   /* Ensure it doesn't expand */
    }
               
        #clear-button {
        background-color: #FF5733;  /* Change to your desired color */
        colr: white;               /* Text color */
        border: none;               /* Optional: Remove border */
        padding: 10px 20px;         /* Optional: Adjust padding */
    }
        #send-button {
        background-color: #007BFF;  /* Blue tone for the Send button */
        color: white;               /* Text color */
        border: none;               /* Optional: Remove border */
        padding: 10px 20px;         /* Optional: Adjust padding */
    }

""") as oekotex_app:
    
    # States for conversation history and options-panel visibility.
    chat_state = gr.State([])         # List of [user, assistant] pairs.
    options_visible = gr.State(False)  # Controls options panel visibility.
    
    # Button to toggle the options panel.
   # toggle_btn = gr.Button("Options", elem_id="toggle_btn")
    with gr.Row():
    # Options panel with parameters.
        with gr.Column(elem_id="options_panel") as options_panel:
            with gr.Accordion("Options", open=False):
                model_dropdown = gr.Dropdown(
                    choices=available_models,
                    value=available_models[0] if available_models else "llama3.2:latest",
                    label="Model"
                )
                temperature_input = gr.Number(value=0.7, label="Temperature")
                temperature_input = gr.Slider(0, 1, 0.7, label="Temperature")
                max_tokens_input = gr.Number(value=99999, label="Max Tokens")
                top_k_tokens_input = gr.Number(value=40, label="Top K Tokens (40 = default)")
                system_role_input = gr.Textbox(
                    placeholder="Type a system role message here...",
                    value="You are a helpful assistant.",
                    label="System Role",
                    show_label=True
                )

            with gr.Accordion("OekoTex", open=False):
                oekotex_check = gr.Checkbox(label="OekoTex ON")
                oekotex_product = gr.Textbox(
                    value="Fio Mescla Ne 30/1 100% YAK CM Compact Z L 01000",
                    label="Product",
                    show_label=True
                )
                oekotex_scope = gr.Textbox(
                    "Raw and mélange yarns in Cotton, Yak (except mélange), Cashmere, Silk, Polyamide (including with biodegradable treatment and Nexylon®), Modacrylic (including PyroTex® with flame retardant properties accepted by OEKO-TEX®), Aramid (meta-aramid Teijinconex® and para-aramid Twaron fibres produced with flame retardant products accepted by OEKO-TEX®) and their blends. Dyed yarns in Cotton, Viscose (incl. Bamboo and Lenzing™ FR with flame retardant products accepted by OEKO-TEX®), Modal, Lyocell, Flax, Polyester, Wool and their blends. Raw fibers in Cotton, Viscose (incl. Bamboo), Modal (Seacell™), Lyocell (LENZING™ and SeaCell™), Flax, Silk and Polyester. Dyed fibers in Cotton, Flax, Viscose, Modal, Lyocell and Polyester. Exclusively produced using components pre-certified according to OEKO-TEX® STANDARD 100.",
                    label="Scope",
                    show_label=True
                )
               
                oekotex_system_role_input = gr.Textbox(
                    value="""
                    Follow the RULES, check the PRODUCT against the SCOPE.
                    
                    <RULES>
                    1. Use the DICTIONARY to interpret abbreviations.
                    2. Check whether the PRODUCT falls within the SCOPE.
                    3. Answer only with "Yes" or "No" followed by the percentage confidence.
                    4. Include chain-of-thought reasoning in the response.
                    5. The mention of raw, mélange, and dyed yarns is relevant. 
                    6. mélange yarns are blends of different fibers or only one fiber in different colors.
                    7. All abbreviations are defined in the DICTIONARY for clarity.
                    8. In case of any ambiguity with abbreviations, refer to the DICTIONARY.
                    9. The PRODUCT descriptions follow standard yarn naming conventions.
                    </RULES>

                    <DICTIONARY>
                    Amazonia = Amazonia  
                    PVA = PVA  
                    Milkweed Floss Fiber = Milkweed Floss Fiber  
                    CA = Canhamo  
                    Kapok = Kapok  
                    MPAN = MicroAcrilico  
                    CO = Algodao  
                    CV = Viscose  
                    MPES = MicroPolyester  
                    PA = Poliamida  
                    WA = Angora  
                    MicroModal = MicroModal  
                    N/A = N/A  
                    MCLY = Micro Liocel  
                    CMD = Modal  
                    SE = Seda  
                    WP = Alpaca  
                    LI = Linho  
                    EL = Elastano  
                    MTF = Metalico  
                    AC = Acetato  
                    CUP = Cupro  
                    Multifibras = Multifibras  
                    Banana = Banana  
                    WS = Caxemira  
                    Pineapple = Pineapple  
                    AG = Alginato  
                    WM = Mohair  
                    AR = Aramida  
                    Yak = Yak  
                    PES = Polyester  
                    MAC = Modacrilica  
                    Nettle = Nettle  
                    PAN = Acrilico  
                    Paper Fiber = Paper Fiber  
                    WO = La  
                    CLY = Liocel
                    Fio Mescla = mélange yarn
                    Fio Cru = raw yarn
                    Fio Tinto = dyed yarn
                    </DICTIONARY>
                  
                            """,
                    label="System Role",
                    show_label=True
                )
                oekotex_submit = gr.Button("Submit")

            with gr.Accordion('Load Files', open=True):
                files_system_role_input = gr.Textbox(

               
                    value="""
                    Follow the RULES to achieve the GOALS.

                    <GOALS>

                    1. Input Format:

                        - A JSON array (table) will be provided. Each object (row) in the array includes the columns:
                            - ProductCode
                            - Product
                            - CertificationCode
                            - Scope
                    
                    2. Evaluation Process:

                        - For each row, determine whether the Product falls within the defined Scope.
                    
                    3. Output Requirements:

                        - Add three new columns to each row:
                            - InScope: Should be "YES" if the product falls under the Scope, or "NO" if it does not.
                            - Justification: Provide a concise chain-of-thought explanation that details how the decision was made.
                            - Confidence: Provide a percentage that reflects the certainty of your determination, eg:
                                - Exact term matches in Product and Scope → Confidence = 90-100%.
                                - Partial match (e.g., inferred from context) → Confidence = 60-89%.
                                - Scope description is vague → Confidence = 50-59%.
                    
                    4. Final Response Format:

                        - Return the modified JSON table with the original columns plus InScope, Justification, and Confidence for each row.
                        - Ensure that the entire response is provided strictly in valid JSON format with no additional text or commentary outside the JSON structure.

                    5. Optional Sample Output:

                        [
                        {
                            "Product": "Fio Cru Ne 30/2 100% CO CM Compact S F 01000",
                            "Scope": "Yarn made of 100 cotton in raw white.",
                            "InScope": "YES",
                            "Justification": "The product includes 'Fio Cru' indicating raw yarn and is made of 100 cotton, which meets the scope.",
                            "Confidence": "95%"
                        },
                        { ... }
                        ]

                    </GOALS>
                    

                    <RULES>

                        1. Interpretation Using the DICTIONARY:

                            - Use the provided DICTIONARY to interpret abbreviations (e.g., CO, CLY, PES) and product designations.
                            - In case of any ambiguity with abbreviations or descriptive terms, refer to the DICTIONARY.
                        
                        2. Yarn Type Identification:

                            - Prefixes:
                                - If the product name contains "Fio Cru", classify it as a raw yarn (untreated, not dyed).
                                - If the product name contains "Fio Mescla", classify it as a mélange yarn (blended fibers, potentially a mix of raw and dyed).
                                - If the product name contains "Fio Tinto", classify it as a dyed yarn (pre-dyed fibers).
                            - Implicit Identification:
                                - If none of these explicit prefixes appear, infer the yarn type using contextual cues (such as color descriptors or additional descriptive terms) and the DICTIONARY.
                        
                        3. Scope Matching:

                            - Verify that the yarn’s composition (as indicated by abbreviations and descriptive terms) matches the fiber requirements stated in the Scope.
                            - Ensure that any additional conditions (such as “raw white” or specific fiber blends) are met.
                        
                        4. Handling Ambiguities:

                            - If the product description or composition is ambiguous, note the uncertainty in the Justification and adjust the Confidence percentage accordingly (e.g., use a lower confidence percentage for uncertain cases).
                        
                        5. Confidence Scoring:

                            - Assign a high confidence (e.g., 95–100%) when the product composition and yarn type clearly match the scope.
                            - Use a slightly lower confidence (e.g., around 90%) when there are minor ambiguities or when inference was needed due to missing explicit prefixes.
                        
                        6. Chain-of-Thought Documentation:

                            - For each row, include a brief explanation of how you identified the yarn type, how the composition was matched against the Scope, and any considerations for ambiguity.
                            - Keep the explanation concise but detailed enough to justify your decision.

                    </RULES>

                    <DICTIONARY>
                    Amazonia = Amazonia
                    Definition: A fiber or product designation referring to materials sourced from or associated with the Amazon region. It may indicate origin or specific quality traits tied to that area. 
                    PVA = PVA
                    Definition: Polyvinyl Alcohol; a synthetic polymer often used as a sizing agent or adhesive in textile processing. It helps in binding fibers and improving fabric strength. 
                    Milkweed Floss Fiber = Milkweed Floss Fiber
                    Definition: A natural fiber obtained from the milkweed plant. It is typically light and airy, used in specialty yarns or non-woven textiles. 
                    CA = Canhamo
                    Definition: Refers to a natural fiber derived from the hemp plant. It is known for its strength, durability, and eco-friendly properties. 
                    Kapok = Kapok
                    Definition: A natural, lightweight fiber harvested from the seed pods of the kapok tree. Known for its softness, buoyancy, and insulation properties, it is often used in fill materials and specialty textiles. 
                    MPAN = MicroAcrilico
                    Definition: A micro version of acrylic fiber, characterized by its fine texture. Commonly used in applications requiring soft, lightweight synthetic fibers.  
                    CO = Algodão
                    Definition: Cotton; a natural fiber obtained from the cotton plant. It is known for its softness, breathability, and widespread use in textiles. 
                    CV = Viscose
                    Definition: A regenerated cellulose fiber (commonly called rayon) produced from natural sources like wood pulp. It is valued for its smooth, silk-like texture and drape.  
                    MPES = MicroPolyester
                    Definition: A micro version of polyester fiber, produced with finer filaments to yield a softer hand-feel while maintaining durability and wrinkle resistance. 
                    PA = Poliamida
                    Definition: Polyamide (commonly known as nylon); a synthetic fiber known for its strength, elasticity, and abrasion resistance, frequently used in both apparel and industrial textiles. 
                    WA = Angora
                    Definition: Fiber sourced from Angora rabbits, prized for its exceptional softness, warmth, and lightweight properties. 
                    MicroModal = MicroModal
                    Definition: A refined, micro version of Modal fiber. Derived from beech trees, it offers enhanced softness, breathability, and moisture management compared to standard Modal.  
                    MCLY = Micro Liocel
                    Definition: A micro version of Liocel (lyocell), a sustainable regenerated cellulose fiber known for its softness, moisture management, and environmentally friendly production process.  
                    CMD = Modal
                    Definition: Modal; a type of rayon produced from beech tree pulp. It is known for its smooth texture, high absorbency, and resistance to shrinkage, making it a popular choice in clothing and bedding. 
                    SE = Seda
                    Definition: Silk; a natural protein fiber produced by silkworms. Renowned for its luster, softness, and strength, silk is considered a luxury textile fiber.  
                    WP = Alpaca
                    Definition: Fiber obtained from alpacas. It is highly valued for its softness, warmth, and hypoallergenic qualities, making it a premium natural fiber in textiles.  
                    LI = Linho
                    Definition: Linen; a natural fiber made from the flax plant. Known for its strength, durability, and cool, breathable quality, linen is commonly used in warm-weather clothing and home textiles.  
                    EL = Elastano
                    Definition: Elastane (also known as spandex or Lycra); a synthetic fiber with exceptional elasticity. It is used to provide stretch and recovery in garments and textiles.  
                    MTF = Metalico
                    Definition: Metallic fiber or yarn; typically involves the incorporation of metal filaments to achieve a shiny, reflective, or decorative effect in textiles.  
                    AC = Acetato
                    Definition: Acetate fiber; a semi-synthetic fiber made from cellulose acetate. It is known for its silk-like appearance, soft drape, and high luster. 
                    CUP = Cupro
                    Definition: 	Cupro; a regenerated cellulose fiber made from cotton linter. It is noted for its softness, breathability, and luxurious feel, often used as a silk substitute.  
                    Multifibras = Multifibras
                    Definition: A blend or composite yarn made from two or more different fibers. This combination is used to achieve a balance of properties, such as strength, softness, and durability, tailored to specific end-use requirements. 
                    Banana = Banana
                    Definition: Banana fiber; derived from the pseudo-stem of banana plants. It is recognized for its strength, eco-friendliness, and unique texture, and is used in both traditional and innovative textile applications. 
                    WS = Caxemira
                    Definition: Cashmere; a luxurious natural fiber obtained from cashmere goats. It is celebrated for its exceptional softness, warmth, and insulating properties.  
                    Pineapple = Pineapple
                    Definition: Also known as piña fiber; extracted from pineapple leaves. This natural fiber is used in textiles for its light weight, natural sheen, and eco-friendly qualities.  
                    AG = Alginato
                    Definition: Alginate fiber; derived from seaweed (alginate salts). It is used in specialized textile applications for its unique texture, biodegradability, and sometimes for its functional properties in non-woven fabrics.  
                    WM = Mohair
                    Definition: Mohair; a natural fiber obtained from the Angora goat. It is known for its sheen, luster, and durability, often used in high-quality apparel and upholstery.  
                    AR = Aramida
                    Definition: Aramid fiber; a class of synthetic fibers known for their high strength, heat resistance, and durability. Examples include Kevlar® and Nomex®, used in protective and industrial textiles.  
                    Yak = Yak
                    Definition: Fiber derived from yaks; valued for its warmth, softness, and natural insulating properties, making it suitable for cold-weather garments.  
                    PES = Polyester
                    Definition: Polyester; a widely used synthetic fiber known for its durability, resistance to wrinkles and shrinking, and versatility in a range of textile applications.  
                    MAC = Modacrilica
                    Definition: Modacrylic; a synthetic fiber noted for its flame resistance, softness, and ease of care. It is used in applications where safety and a wool-like appearance are desired. 
                    Nettle = Nettle
                    Definition: Nettle fiber; obtained from the stinging nettle plant. It is an eco-friendly natural fiber, historically used in textiles for its strength and durability.  
                    PAN = Acrilico
                    Definition: Acrylic; a synthetic fiber that mimics the properties of wool. It is lightweight, warm, and resistant to moths, making it popular for knitwear and other apparel.  
                    Paper Fiber = Paper Fiber
                    Definition: Fiber derived from recycled paper or pulp. It is used in specialized textile applications to create unique textures and promote sustainability.  
                    WO = La
                    Definition: Likely shorthand for wool; a natural fiber obtained from sheep. Wool is renowned for its warmth, elasticity, and moisture-wicking properties. (Note: “La” is presumed to indicate wool in this context.)   
                    CLY = Liocel
                    Definition: A regenerated cellulose fiber. Note: When a product is listed as “100% CLY,” it is not considered cotton even if its appearance is similar.
                    Fio Cru = raw yarn
                    Definition: Yarn produced from fibers that have not been dyed or treated beyond basic spinning. Typically used for yarns intended to remain in their natural color.
                    Fio Mescla = mélange yarn
                    Definition: Yarn produced by blending fibers that may be raw and/or dyed, resulting in a variegated or mixed-color effect.
                    Fio Tinto = dyed yarn
                    Definition: Yarn produced from fibers that have been pre-dyed before spinning, resulting in a uniform color.
                    </DICTIONARY>
                  


                            """,
                    label="System Role",
                    show_label=True
                )
                product_file =  gr.File(label="Upload Product File")
                certification_file =  gr.File(label="Upload Scope File")
                load_files_submit =  gr.Button("Process Files")




        # Chatbot display and user input area.
        with gr.Column():
            chatbot = gr.Chatbot(label="Chat", type="messages")
            with gr.Row():
                user_input_box = gr.Textbox(
                    placeholder="Type your message here...",
                    label="Your Message",
                    show_label=False
                )
            with gr.Row():
                send_button = gr.Button("Send", elem_id="send-button")
                clear_button = gr.Button("Clear", elem_id="clear-button")
        
    # Wire the send button and Enter-key submission to process the chat.
    send_button.click(
        process_chat, 
        inputs=[
            user_input_box, chat_state, 
            model_dropdown, temperature_input, 
            max_tokens_input, top_k_tokens_input, system_role_input
        ],
        outputs=[user_input_box, chat_state, chatbot]
    )

    clear_button.click(clear_chat, 
                       inputs=None, 
                       outputs=[chatbot, chat_state])
    
    user_input_box.submit(
        process_chat, 
        inputs=[
            user_input_box, chat_state, 
            model_dropdown, temperature_input, 
            max_tokens_input, top_k_tokens_input, system_role_input
        ],
        outputs=[user_input_box, chat_state, chatbot]
    )


    oekotex_submit.click(
        combine_oekotex_inputs, 
        inputs=[
            oekotex_product, oekotex_scope, chat_state, 
            model_dropdown, temperature_input, 
            max_tokens_input, top_k_tokens_input, oekotex_system_role_input
        ],
        outputs=[user_input_box, chat_state, chatbot]
    )

    load_files_submit.click(
        start_loading_files,
        inputs=[product_file, certification_file,chat_state, 
            model_dropdown, temperature_input, 
            max_tokens_input, top_k_tokens_input, files_system_role_input],
            
        outputs=[user_input_box, chat_state, chatbot]
    )



if __name__ == "__main__":
    oekotex_app.launch()
