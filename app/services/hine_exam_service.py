from app.services.exam_service import ExamService
from app.services.section_service import SectionService
from app.services.item_service import ItemService
from sqlmodel import Session
from app.database.database import engine
from app.schemas.hine_exam import HineExamCreate
from fastapi import HTTPException, status
from app.schemas.exam import CreateExam

class HineExamService:
    def __init__(self):
        self.exam_service = ExamService()
        self.section_service = SectionService()
        self.item_service = ItemService()

    def create_exam(self, hineExam: HineExamCreate):
        children_id= hineExam.children_id
        doctor_id= hineExam.doctor_id
        try:
            #Creating Exam
            exam = self.exam_service.create_exam({
            "name": "Hine Exam",
            "eliminated":False,
            "description": hineExam.general_description,
            "child_id": children_id, 
            doctor_id: doctor_id
        })
            #Creating sections
            cranial_nerves_section = self.section_service.create_section({
            "section_name": "pares craneales",
            "id_exam": exam.id
                })
            posture_section = self.section_service.create_section({
            "section_name": "postura",
            "id_exam": exam.id
                })
            movement_section = self.section_service.create_section({
            "section_name": "movimiento",
            "id_exam": exam.id
                })
            tone_section = self.section_service.create_section({
            "section_name": "tono",
            "id_exam": exam.id
                })
            reflexes_reactions_section =self.section_service.create_section({
            "section_name": "reflejos y reacciones",
            "id_exam": exam.id
                })
            motor_milestones_section = self.section_service.create_section({
            "section_name": "hitos motores",
            "id_exam": exam.id
                })
            behavior_section= self.section_service.create_section({
            "section_name": "comportamiento",
            "id_exam": exam.id
                })
            
            #Cranial Nerves
            simple_appearance =self.item_service.create_item({
                    "title": "apariencia facial",
                    "score": hineExam.cranial_nerves_simple_appearance_score,
                    "description": hineExam.cranial_nerves_simple_appearance_description,
                    "right_asimetric_count" : hineExam.cranial_nerves_simple_appearance_r_asimetric_count,
                    "left_asimetric_count": hineExam.cranial_nerves_simple_appearance_l_asimetric_count,
                    "section_id": cranial_nerves_section.id
            })
            eye_movement = self.item_service.create_item({
                "title": "movimientos oculares",
                    "score": hineExam.cranial_nerves_eye_movement_score,
                    "description": hineExam.cranial_nerves_eye_movement_description,
                    "right_asimetric_count" : hineExam.cranial_nerves_eye_movement_r_asimetric_count,
                    "left_asimetric_count": hineExam.cranial_nerves_eye_movement_l_asimetric_count,
                    "section_id": cranial_nerves_section.id
            })
            visual_response =self.item_service.create_item({
                    "title": "respuesta visual",
                    "score": hineExam.cranial_nerves_visual_response_score,
                    "description": hineExam.cranial_nerves_visual_response_description,
                    "right_asimetric_count" : hineExam.cranial_nerves_visual_response_r_asimetric_count,
                    "left_asimetric_count": hineExam.cranial_nerves_visual_response_l_asimetric_count,
                    "section_id": cranial_nerves_section.id
            })
            
            auditory = self.item_service.create_item({
                    "title": "respuesta auditiva",
                    "score": hineExam.cranial_nerves_auditory_response_score,
                    "description": hineExam.cranial_nerves_auditory_response_description,
                    "right_asimetric_count" : hineExam.cranial_nerves_auditory_response_r_asimetric_count,
                    "left_asimetric_count": hineExam.cranial_nerves_auditory_response_l_asimetric_count,
                    "section_id": cranial_nerves_section.id
            })
            sucking_swallowing = self.item_service.create_item({
                    "title": "succion / deglucion",
                    "score": hineExam.cranial_nerves_sucking_swallowing_score,
                    "description": hineExam.cranial_nerves_sucking_swallowing_description,
                    "right_asimetric_count" : hineExam.cranial_nerves_sucking_swallowing_r_asimetric_count,
                    "left_asimetric_count": hineExam.cranial_nerves_sucking_swallowing_l_asimetric_count,
                    "section_id": cranial_nerves_section.id
            })
            #Posture
            head = self.item_service.create_item({
                "title": "cabeza",
                    "score": hineExam.posture_head_score,
                    "description": hineExam.posture_head_description,
                    "right_asimetric_count" : hineExam.posture_head_r_asimetric_count,
                    "left_asimetric_count": hineExam.posture_head_l_asimetric_count,
                    "section_id": posture_section.id
            })
            trunk = self.item_service.create_item(
                {
                "title": "tronco",
                    "score": hineExam.posture_trunk_score,
                    "description": hineExam.posture_trunk_description,
                    "right_asimetric_count" : hineExam.posture_trunk_r_asimetric_count,
                    "left_asimetric_count": hineExam.posture_trunk_l_asimetric_count,
                    "section_id": posture_section.id
            }
            )
            arms = self.item_service.create_item({
                "title": "brazos",
                    "score": hineExam.posture_arms_score,
                    "description": hineExam.posture_arms_description,
                    "right_asimetric_count" : hineExam.posture_arms_r_asimetric_count,
                    "left_asimetric_count": hineExam.posture_arms_l_asimetric_count,
                    "section_id": posture_section.id
            })
            hands = self.item_service.create_item(
                {
                "title": "manos",
                    "score": hineExam.posture_hands_score,
                    "description": hineExam.posture_hands_description,
                    "right_asimetric_count" : hineExam.posture_hands_r_asimetric_count,
                    "left_asimetric_count": hineExam.posture_hands_l_asimetric_count,
                    "section_id": posture_section.id
            }
            )
            legs = self.item_service.create_item(
                {
                "title": "piernas",
                    "score": hineExam.posture_legs_score,
                    "description": hineExam.posture_legs_description,
                    "right_asimetric_count" : hineExam.posture_legs_r_asimetric_count,
                    "left_asimetric_count": hineExam.posture_legs_l_asimetric_count,
                    "section_id": posture_section.id
            }
            )
            feet = self.item_service.create_item(
                {
                "title": "pies",
                    "score": hineExam.posture_feet_score,
                    "description": hineExam.posture_feet_description,
                    "right_asimetric_count" : hineExam.posture_feet_r_asimetric_count,
                    "left_asimetric_count": hineExam.posture_feet_l_asimetric_count,
                    "section_id": posture_section.id
            }
            )
            #Movement
            amount = self.item_service.create_item(
                {
                "title": "cantidad",
                    "score": hineExam.movement_amount_score,
                    "description": hineExam.movement_amount_description,
                    "right_asimetric_count" : hineExam.movement_amount_r_asimetric_count,
                    "left_asimetric_count": hineExam.movement_amount_l_asimetric_count,
                    "section_id": movement_section.id
            }
            )
            quality = self.item_service.create_item(
            {
                "title": "calidad",
                    "score": hineExam.movement_quality_score,
                    "description": hineExam.movement_quality_description,
                    "right_asimetric_count" : hineExam.movement_quality_r_asimetric_count,
                    "left_asimetric_count": hineExam.movement_quality_l_asimetric_count,
                    "section_id": movement_section.id
            }
            )
            #Tone
            scarf_sign  = self.item_service.create_item(
                {
                "title": "signo de la bufanda",
                    "score": hineExam.tone_scarf_sign_score,
                    "description": hineExam.tone_scarf_sign_description,
                    "right_asimetric_count" : hineExam.tone_scarf_sign_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_scarf_sign_l_asimetric_count,
                    "section_id": tone_section.id
            }
            )
            passive_shoulder_elevation = self.item_service.create_item(
                {
                "title": "elevacion pasiva del hombro",
                    "score": hineExam.tone_passive_shoulder_elevation_score,
                    "description": hineExam.tone_passive_shoulder_elevation_description,
                    "right_asimetric_count" : hineExam.tone_passive_shoulder_elevation_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_passive_shoulder_elevation_l_asimetric_count,
                    "section_id": tone_section.id
            }
            )
            pronation_supination = self.item_service.create_item(
                                {
                "title": "pronacion / supinacion",
                    "score": hineExam.tone_pronation_supination_score,
                    "description": hineExam.tone_pronation_supination_description,
                    "right_asimetric_count" : hineExam.tone_pronation_supination_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_pronation_supination_l_asimetric_count,
                    "section_id": tone_section.id
            }
            )
            hip_adduction = self.item_service.create_item(
                {
                "title": "aductores de cadera",
                    "score": hineExam.tone_hip_adduction_score,
                    "description": hineExam.tone_hip_adduction_description,
                    "right_asimetric_count" : hineExam.tone_hip_adduction_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_hip_adduction_l_asimetric_count,
                    "section_id": tone_section.id
            }
            )
            popliteal_angle = self.item_service.create_item(
                                {
                "title": "angulo popliteo",
                    "score": hineExam.tone_popliteal_angle_score,
                    "description": hineExam.tone_popliteal_angle_description,
                    "right_asimetric_count" : hineExam.tone_popliteal_angle_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_popliteal_angle_l_asimetric_count,
                    "section_id": tone_section.id
            }
            )
            ankle_dorsiflexion = self.item_service.create_item(
                {
                "title": "dorsiflexion de tobillo",
                    "score": hineExam.tone_ankle_dorsiflexion_score,
                    "description": hineExam.tone_ankle_dorsiflexion_description,
                    "right_asimetric_count" : hineExam.tone_ankle_dorsiflexion_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_ankle_dorsiflexion_l_asimetric_count,
                    "section_id": tone_section.id
            }
            )
            pull_to_sit = self.item_service.create_item({
                "title": "pull to sit",
                    "score": hineExam.tone_pull_to_sit_score,
                    "description": hineExam.tone_pull_to_sit_description,
                    "right_asimetric_count" : hineExam.tone_pull_to_sit_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_pull_to_sit_l_asimetric_count,
                    "section_id": tone_section.id
            })
            ventral_suspension = self.item_service.create_item({
                "title": "suspension ventral",
                    "score": hineExam.tone_ventral_suspension_score,
                    "description": hineExam.tone_ventral_suspension_description,
                    "right_asimetric_count" : hineExam.tone_ventral_suspension_r_asimetric_count,
                    "left_asimetric_count": hineExam.tone_ventral_suspension_l_asimetric_count,
                    "section_id": tone_section.id
            })
            #Reflexes and Reactions
            arm_protecting = self.item_service.create_item({
                "title": "proteccion del brazo",
                    "score": hineExam.reflexes_reactions_arm_protecting_score,
                    "description": hineExam.reflexes_reactions_arm_protecting_description,
                    "right_asimetric_count" : hineExam.reflexes_reactions_arm_protecting_r_asimetric_count,
                    "left_asimetric_count": hineExam.reflexes_reactions_arm_protecting_l_asimetric_count,
                    "section_id": reflexes_reactions_section.id
            })
            vertical_suspension = self.item_service.create_item({
                "title": "suspension vertical",
                    "score": hineExam.reflexes_reactions_vertical_suspension_score,
                    "description": hineExam.reflexes_reactions_vertical_suspension_description,
                    "right_asimetric_count" : hineExam.reflexes_reactions_vertical_suspension_r_asimetric_count,
                    "left_asimetric_count": hineExam.reflexes_reactions_vertical_suspension_l_asimetric_count,
                    "section_id": reflexes_reactions_section.id
            })
            lateral_suspension = self.item_service.create_item({
                "title": "suspension lateral",
                    "score": hineExam.reflexes_reactions_lateral_suspension_score,
                    "description": hineExam.reflexes_reactions_lateral_suspension_description,
                    "right_asimetric_count" : hineExam.reflexes_reactions_lateral_suspension_r_asimetric_count,
                    "left_asimetric_count": hineExam.reflexes_reactions_lateral_suspension_l_asimetric_count,
                    "section_id": reflexes_reactions_section.id
            })
            parachute = self.item_service.create_item({
                "title": "paracaidas",
                    "score": hineExam.reflexes_reactions_parachute_score,
                    "description": hineExam.reflexes_reactions_parachute_description,
                    "right_asimetric_count" : hineExam.reflexes_reactions_parachute_r_asimetric_count,
                    "left_asimetric_count": hineExam.reflexes_reactions_parachute_l_asimetric_count,
                    "section_id": reflexes_reactions_section.id
            })
            tendon_reflexes = self.item_service.create_item({
                "title": "reflejos tendinosos",
                    "score": hineExam.reflexes_reactions_tendon_reflexes_score,
                    "description": hineExam.reflexes_reactions_tendon_reflexes_description,
                    "right_asimetric_count" : hineExam.reflexes_reactions_tendon_reflexes_r_asimetric_count,
                    "left_asimetric_count": hineExam.reflexes_reactions_tendon_reflexes_l_asimetric_count,
                    "section_id": reflexes_reactions_section.id
            })
            #Motor Milestones
            head_control = self.item_service.create_item({
                "title": "control cefalico",
                "score":hineExam.motor_milestones_head_control_age_achieved,
                "description": hineExam.motor_milestones_head_control_observation,
                "right_asimetric_count": hineExam.motor_milestones_head_control_observation_r_asimetric_count,
                "left_asimetric_count":hineExam.motor_milestones_head_control_observation_r_asimetric_count,
                "section_id": motor_milestones_section.id
            })
            sitting = self.item_service.create_item({
                "title": "sedestacion",
                "score":hineExam.motor_milestones_sitting_age_achieved,
                "description": hineExam.motor_milestones_sitting_observation,
                "right_asimetric_count": hineExam.motor_milestones_sitting_observation_r_asimetric_count,
                "left_asimetric_count":hineExam.motor_milestones_sitting_observation_l_asimetric_count,
                "section_id": motor_milestones_section.id
            })
            voluntary_gasping = self.item_service.create_item({
                "title": "agarre voluntario",
                "score":hineExam.motor_milestones_voluntary_gasping_age_achieved,
                "description": "Lado: "+hineExam.motor_milestones_voluntary_gasping_side+"\n"+hineExam.motor_milestones_voluntary_gasping_observation,
                "right_asimetric_count": hineExam.motor_milestones_voluntary_gasping_observation_r_asi_count,
                "left_asimetric_count":hineExam.motor_milestones_voluntary_gasping_observation_l_asi_count,
                "section_id": motor_milestones_section.id
            })
            ability_to_kick_supine = self.item_service.create_item({
                "title": "patalear en supino",
                "score":hineExam.motor_milestones_ability_to_kick_supine_age_achieved,
                "description": hineExam.motor_milestones_ability_to_kick_supine_observation,
                "right_asimetric_count": hineExam.motor_milestones_ability_to_kick_supine_obs_r_asi_count,
                "left_asimetric_count":hineExam.motor_milestones_ability_to_kick_supine_obs_l_asi_count,
                "section_id": motor_milestones_section.id
            })
            
            rolling_over = self.item_service.create_item({
                "title": "volteo",
                "score":hineExam.motor_milestones_rolling_over_age_achieved,
                "description": "Lado: "+hineExam.motor_milestones_rolling_over_side+"\n"+hineExam.motor_milestones_rolling_over_observation,
                "right_asimetric_count": hineExam.motor_milestones_rolling_over_observation_r_asimetric_count,
                "left_asimetric_count":hineExam.motor_milestones_rolling_over_observation_l_asimetric_count,
                "section_id": motor_milestones_section.id
            })
            crawling = self.item_service.create_item({
                "title": "gateo",
                "score":hineExam.motor_milestones_crawling_age_achieved,
                "description": "Arrastra las Nalgas: "+hineExam.motor_milestones_crawling_scooting_on_the_bottom+"\n"+hineExam.motor_milestones_crawling_observation,
                "right_asimetric_count": hineExam.motor_milestones_crawling_observation_r_asimetric_count,
                "left_asimetric_count":hineExam.motor_milestones_crawling_observation_l_asimetric_count,
                "section_id": motor_milestones_section.id
            })
            bipedalism = self.item_service.create_item({
                "title": "bipedestacion",
                "score":hineExam.motor_milestones_bipedalism_age_achieved,
                "description": hineExam.motor_milestones_bipedalism_observation,
                "right_asimetric_count": hineExam.motor_milestones_bipedalism_observation_r_asimetric_count,
                "left_asimetric_count":hineExam.motor_milestones_bipedalism_observation_l_asimetric_count,
                "section_id": motor_milestones_section.id
            }) 
            gait = self.item_service.create_item({
                "title": "marcha",
                "score":hineExam.motor_milestones_gait_age_achieved,
                "description": hineExam.motor_milestones_gait_observation,
                "right_asimetric_count": hineExam.motor_milestones_gait_observation_l_asimetric_count,
                "left_asimetric_count":hineExam.motor_milestones_gait_observation_r_asimetric_count,
                "section_id": motor_milestones_section.id
            })
            #Behavior
            state_of_consciousness = self.item_service.create_item(
                {
                "title": "estado de consciencia",
                "score":hineExam.behavior_emotional_state_score,
                "description": hineExam.behavior_emotional_state_description,
                "right_asimetric_count": None,
                "left_asimetric_count":None,
                "section_id": behavior_section.id
            }
            )
            emotional_state =  self.item_service.create_item(
                {
                "title": "estado emocional",
                "score":hineExam.behavior_emotional_state_score,
                "description": hineExam.behavior_emotional_state_description,
                "right_asimetric_count": None,
                "left_asimetric_count":None,
                "section_id": behavior_section.id
            }
            )
            social_interaction = self.item_service.create_item(
            {
                "title": "interaccion social",
                "score":hineExam.behavior_social_interaction_score,
                "description": hineExam.behavior_state_of_consciousness_description,
                "right_asimetric_count": None,
                "left_asimetric_count":None,
                "section_id": behavior_section.id
            }
            )
            
        
        except HTTPException as e:
            raise e
        



        


            
