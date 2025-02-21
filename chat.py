import gradio as gr
import os
from openai_cli.cli_openai import fetch_model_choices, process_chat
from scripts.loading_files import load_files_to_json

with open('rules.txt', 'r', encoding='utf-8') as file:
    rules = file.read()

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
                    value = rules
               
                   ,
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






