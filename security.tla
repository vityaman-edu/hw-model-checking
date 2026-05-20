-------------------------------- MODULE security ----------------------------------
EXTENDS Integers

CONSTANTS GATE

VARIABLES isGateInvaded,
          isButtonPressed,
          isSecurityOnSite,
          isSystemAlarmed,
          isGateLocked

vars ==
  << isGateInvaded,
     isButtonPressed,
     isSecurityOnSite,
     isSystemAlarmed,
     isGateLocked
  >>

TypeOK ==
  /\ isGateInvaded \in [GATE -> BOOLEAN]
  /\ isButtonPressed \in BOOLEAN
  /\ isSecurityOnSite \in BOOLEAN
  /\ isSystemAlarmed \in BOOLEAN
  /\ isGateLocked \in [GATE -> BOOLEAN]

-----------------------------------------------------------------------------------

IsAnyGateInvaded == \E g \in GATE: isGateInvaded[g]

-----------------------------------------------------------------------------------

EventInvasionToggled(g) ==
  /\ isGateInvaded' = [isGateInvaded EXCEPT ![g] = ~isGateInvaded[g]]
  /\ UNCHANGED << isButtonPressed,
        isSecurityOnSite,
        isSystemAlarmed,
        isGateLocked
     >>

EventSomeInvasionToggled == \E g \in GATE: EventInvasionToggled(g)

EventButtonToggled ==
  /\ isButtonPressed' = ~isButtonPressed
  /\ UNCHANGED << isGateInvaded,
        isSecurityOnSite,
        isSystemAlarmed,
        isGateLocked
     >>

EventAlarmStart ==
  /\ ~isSystemAlarmed
  /\ ( IsAnyGateInvaded \/ isButtonPressed )
  /\ isSystemAlarmed' = TRUE
  /\ isGateLocked' = [g \in GATE |-> TRUE]
  /\ UNCHANGED << isGateInvaded, isButtonPressed, isSecurityOnSite >>

EventAlarmStop ==
  /\ isSystemAlarmed
  /\ ( isSecurityOnSite \/ ~isButtonPressed )
  /\ isSystemAlarmed' = FALSE
  /\ isGateLocked' = [g \in GATE |-> FALSE]
  /\ UNCHANGED << isGateInvaded, isButtonPressed, isSecurityOnSite >>

EventSecurityArrived ==
  /\ ~isSecurityOnSite
  /\ isSystemAlarmed
  /\ isSecurityOnSite' = TRUE
  /\ UNCHANGED << isGateInvaded,
        isButtonPressed,
        isSystemAlarmed,
        isGateLocked
     >>

EventSecurityLeaved ==
  /\ isSecurityOnSite
  /\ ~isSystemAlarmed
  /\ isSecurityOnSite' = FALSE
  /\ UNCHANGED << isGateInvaded,
        isButtonPressed,
        isSystemAlarmed,
        isGateLocked
     >>

-----------------------------------------------------------------------------------

Init ==
  /\ isGateInvaded = [g \in GATE |-> FALSE]
  /\ isButtonPressed = FALSE
  /\ isSecurityOnSite = FALSE
  /\ isSystemAlarmed = FALSE
  /\ isGateLocked = [g \in GATE |-> FALSE]

Next ==
  \/ EventSomeInvasionToggled
  \/ EventButtonToggled
  \/ EventAlarmStart
  \/ EventAlarmStop
  \/ EventSecurityArrived
  \/ EventSecurityLeaved

-----------------------------------------------------------------------------------

PropertyAlarmLocksGates ==
  isSystemAlarmed <=> ( \A g \in GATE: isGateLocked[g] )

PropertyAlarmStart ==
  [][( ~isSystemAlarmed /\ isSystemAlarmed' ) =>
    ( IsAnyGateInvaded \/ isButtonPressed )]_vars

PropertyAlarmStop ==
  [][( isSystemAlarmed /\ ~isSystemAlarmed' ) =>
    ( isSecurityOnSite \/ ~isButtonPressed )]_vars

PropertySecurityOnlyOnAlarm ==
  [][( ~isSecurityOnSite /\ isSecurityOnSite' ) => isSystemAlarmed]_vars

===================================================================================
