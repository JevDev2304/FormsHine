
from pydantic import BaseModel, ConfigDict
from typing import Optional


class HineExam(BaseModel):

    children_id: str 
    doctor_id: str
    exam_date: str
    general_description: str = ""

    cranial_nerves_simple_appearance_score: int 
    cranial_nerves_simple_appearance_description: Optional[str] = None
    cranial_nerves_simple_appearance_r_asimetric_count: int = 0
    cranial_nerves_simple_appearance_l_asimetric_count: int = 0

    cranial_nerves_eye_movement_score: int = 0
    cranial_nerves_eye_movement_description: Optional[str] = None
    cranial_nerves_eye_movement_r_asimetric_count: int = 0
    cranial_nerves_eye_movement_l_asimetric_count: int = 0

    cranial_nerves_visual_response_score: int = 0
    cranial_nerves_visual_response_description: Optional[str] = None
    cranial_nerves_visual_response_r_asimetric_count: int = 0
    cranial_nerves_visual_response_l_asimetric_count: int = 0

    cranial_nerves_auditory_response_score: int = 0
    cranial_nerves_auditory_response_description: Optional[str] = None
    cranial_nerves_auditory_response_r_asimetric_count: int = 0
    cranial_nerves_auditory_response_l_asimetric_count: int = 0

    cranial_nerves_sucking_swallowing_score: int = 0
    cranial_nerves_sucking_swallowing_description: Optional[str] = None
    cranial_nerves_sucking_swallowing_r_asimetric_count: int = 0
    cranial_nerves_sucking_swallowing_l_asimetric_count: int = 0

    # Posture
    posture_head_score: int = 0
    posture_head_description: Optional[str] = None
    posture_head_r_asimetric_count: int = 0
    posture_head_l_asimetric_count: int = 0

    posture_trunk_score: int = 0
    posture_trunk_description: Optional[str] = None
    posture_trunk_r_asimetric_count: int = 0
    posture_trunk_l_asimetric_count: int = 0

    posture_arms_score: int = 0
    posture_arms_description: Optional[str] = None
    posture_arms_r_asimetric_count: int = 0
    posture_arms_l_asimetric_count: int = 0
    
    posture_hands_score: int = 0
    posture_hands_description: Optional[str] = None
    posture_hands_r_asimetric_count: int = 0
    posture_hands_l_asimetric_count: int = 0

    posture_legs_score: int = 0
    posture_legs_description: Optional[str] = None
    posture_legs_r_asimetric_count: int = 0
    posture_legs_l_asimetric_count: int = 0

    posture_feet_score: int = 0
    posture_feet_description: Optional[str] = None
    posture_feet_r_asimetric_count: int = 0
    posture_feet_l_asimetric_count: int = 0

    # Movement
    movement_amount_score: int = 0
    movement_amount_description: Optional[str] = None
    movement_amount_r_asimetric_count: int = 0
    movement_amount_l_asimetric_count: int = 0

    movement_quality_score: int = 0
    movement_quality_description: Optional[str] = None
    movement_quality_r_asimetric_count: int = 0
    movement_quality_l_asimetric_count: int = 0

    # Tone
    tone_scarf_sign_score: int = 0
    tone_scarf_sign_description: Optional[str] = None
    tone_scarf_sign_r_asimetric_count: int = 0
    tone_scarf_sign_l_asimetric_count: int = 0

    tone_passive_shoulder_elevation_score: int = 0
    tone_passive_shoulder_elevation_description: Optional[str] = None
    tone_passive_shoulder_elevation_r_asimetric_count: int = 0
    tone_passive_shoulder_elevation_l_asimetric_count: int = 0

    tone_pronation_supination_score: int = 0
    tone_pronation_supination_description: Optional[str] = None
    tone_pronation_supination_r_asimetric_count: int = 0
    tone_pronation_supination_l_asimetric_count: int = 0

    tone_hip_adduction_score: int = 0
    tone_hip_adduction_description: Optional[str] = None
    tone_hip_adduction_r_asimetric_count: int = 0
    tone_hip_adduction_l_asimetric_count: int = 0

    tone_popliteal_angle_score: int = 0
    tone_popliteal_angle_description: Optional[str] = None
    tone_popliteal_angle_r_asimetric_count: int = 0
    tone_popliteal_angle_l_asimetric_count: int = 0

    tone_ankle_dorsiflexion_score: int = 0
    tone_ankle_dorsiflexion_description: Optional[str] = None
    tone_ankle_dorsiflexion_r_asimetric_count: int = 0
    tone_ankle_dorsiflexion_l_asimetric_count: int = 0

    tone_pull_to_sit_score: int = 0
    tone_pull_to_sit_description: Optional[str] = None
    tone_pull_to_sit_r_asimetric_count: int = 0
    tone_pull_to_sit_l_asimetric_count: int = 0

    tone_ventral_suspension_score: int = 0
    tone_ventral_suspension_description: Optional[str] = None
    tone_ventral_suspension_r_asimetric_count: int = 0
    tone_ventral_suspension_l_asimetric_count: int = 0

    # Reflexes and Reactions
    reflexes_reactions_arm_protecting_score: int = 0
    reflexes_reactions_arm_protecting_description: Optional[str] = None
    reflexes_reactions_arm_protecting_r_asimetric_count: int = 0
    reflexes_reactions_arm_protecting_l_asimetric_count: int = 0

    reflexes_reactions_vertical_suspension_score: int = 0
    reflexes_reactions_vertical_suspension_description: Optional[str] = None
    reflexes_reactions_vertical_suspension_r_asimetric_count: int = 0
    reflexes_reactions_vertical_suspension_l_asimetric_count: int = 0

    reflexes_reactions_lateral_suspension_score: int = 0
    reflexes_reactions_lateral_suspension_description: Optional[str] = None
    reflexes_reactions_lateral_suspension_r_asimetric_count: int = 0
    reflexes_reactions_lateral_suspension_l_asimetric_count: int = 0

    reflexes_reactions_parachute_score: int = 0
    reflexes_reactions_parachute_description: Optional[str] = None
    reflexes_reactions_parachute_r_asimetric_count: int = 0
    reflexes_reactions_parachute_l_asimetric_count: int = 0

    reflexes_reactions_tendon_reflexes_score: int = 0
    reflexes_reactions_tendon_reflexes_description: Optional[str] = None
    reflexes_reactions_tendon_reflexes_r_asimetric_count: int = 0
    reflexes_reactions_tendon_reflexes_l_asimetric_count: int = 0

    # Motor Milestones
    motor_milestones_head_control_observation: Optional[str] = None
    motor_milestones_head_control_age_achieved: int = 0
    motor_milestones_head_control_observation_r_asimetric_count: int = 0
    motor_milestones_head_control_observation_l_asimetric_count: int = 0

    motor_milestones_sitting_observation: Optional[str] = None
    motor_milestones_sitting_age_achieved: int = 0
    motor_milestones_sitting_observation_r_asimetric_count: int = 0
    motor_milestones_sitting_observation_l_asimetric_count: int = 0

    motor_milestones_voluntary_gasping_observation: Optional[str] = None
    motor_milestones_voluntary_gasping_side: Optional[str] = None
    motor_milestones_voluntary_gasping_age_achieved: int = 0
    motor_milestones_voluntary_gasping_observation_r_asi_count: int = 0
    motor_milestones_voluntary_gasping_observation_l_asi_count: int = 0

    motor_milestones_ability_to_kick_supine_observation: Optional[str] = None
    motor_milestones_ability_to_kick_supine_age_achieved: int = 0
    motor_milestones_ability_to_kick_supine_obs_r_asi_count: int = 0
    motor_milestones_ability_to_kick_supine_obs_l_asi_count: int = 0

    motor_milestones_rolling_over_observation: Optional[str] = None
    motor_milestones_rolling_over_side: Optional[str] = None
    motor_milestones_rolling_over_age_achieved: int = 0
    motor_milestones_rolling_over_observation_r_asimetric_count: int = 0
    motor_milestones_rolling_over_observation_l_asimetric_count: int = 0

    motor_milestones_crawling_observation: Optional[str] = None
    motor_milestones_crawling_scooting_on_the_bottom: bool = False
    motor_milestones_crawling_age_achieved: int = 0
    motor_milestones_crawling_observation_r_asimetric_count: int = 0
    motor_milestones_crawling_observation_l_asimetric_count: int = 0

    motor_milestones_bipedalism_observation: Optional[str] = None
    motor_milestones_bipedalism_age_achieved: int = 0
    motor_milestones_bipedalism_observation_r_asimetric_count: int = 0
    motor_milestones_bipedalism_observation_l_asimetric_count: int = 0

    motor_milestones_gait_observation: Optional[str] = None
    motor_milestones_gait_age_achieved: int = 0
    motor_milestones_gait_observation_r_asimetric_count: int = 0
    motor_milestones_gait_observation_l_asimetric_count: int = 0

    # Behavior
    behavior_state_of_consciousness_score: int = 0
    behavior_state_of_consciousness_description: Optional[str] = None

    behavior_emotional_state_score: int = 0
    behavior_emotional_state_description: Optional[str] = None

    behavior_social_interaction_score: int = 0
    behavior_social_interaction_description: Optional[str] = None




    model_config = ConfigDict(from_attributes=True)
